import json
import os
import random
import requests
import time
from datetime import datetime, timedelta
from threading import Thread
from fastapi import FastAPI, HTTPException, Header, BackgroundTasks, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from docker import DockerClient
import docker.types
import dotenv
import subprocess
import yaml


dotenv.load_dotenv()
app = FastAPI()

# Define the auth_scheme using HTTPBearer
auth_scheme = HTTPBearer()
# Load environment variables
ssh_user = os.getenv("DOCKER_SSH_USER")
ssh_key_path = "/root/.ssh/id_rsa"
ssh_host = os.getenv("DOCKER_SSH_HOST")
cors_origins = os.getenv("API_CORS_ORIGIN").split(",")
# Define our static folder, where will be our svelte build later
app.mount("/dashboard", StaticFiles(directory="public"), name="dashboard")
app.mount("/_app", StaticFiles(directory="public/_app"), name="_app")

# Prediction object to store current prediction details
current_prediction = {}

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



def add_ssh_host_key(hostname):
    print(f" 🔑 Adding SSH host key for {hostname}...")
    # Adds the SSH host key for the given hostname to the known_hosts file
    known_hosts_path = "/root/.ssh/known_hosts"
    subprocess.run(["ssh-keyscan", "-H", hostname], stdout=open(known_hosts_path, "a"))


add_ssh_host_key(ssh_host)

client = DockerClient(base_url=f"ssh://{ssh_user}@{ssh_host}" if ssh_key_path else "unix://var/run/docker.sock")


# Initialize jobs dictionary
jobs = {}


def load_config():
    with open("../data/config.yaml", "r") as file:
        return yaml.safe_load(file)

config = load_config()


def authenticate(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme), request: str = None):
    token = credentials.credentials
    for entry in config['tokens']:
        if token == entry['token']:
            current_prediction['user'] = entry['name']  # Assuming 'name' field in tokens
            return True
    raise HTTPException(status_code=403, detail="Not Authorized")

def verify_scope(token: str,image: str):
    for entry in config['tokens']:
        print(f" 🔒 Verifying scope for token {token} and image {image}")
        if token == entry['token']:
            print(f" ### 🔒 Verifying scope for token {token} and image {image}")
            if image in entry['scope'] or "*" in entry['scope']:
                return True
    raise HTTPException(status_code=403, detail="Not Authorized")

def load_jobs():
    try:
        with open("../data/jobs.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


jobs = load_jobs()

def save_jobs():
    with open("../data/jobs.json", "w") as file:
        json.dump(jobs, file, indent=4)

def update_prediction_file():
    try:
        with open("../data/predictions.json", "r") as file:
            predictions = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        predictions = []
    
    predictions.append(current_prediction.copy())
    
    with open("../data/predictions.json", "w") as file:
        json.dump(predictions, file, indent=4)


def get_container_by_image(image):
    for container in client.containers.list(all=True):
        if container.attrs["Config"]["Image"] == image:
            return container
    return None


def start_or_restart_container(container, image):
    if container.status == "exited":
        print(f" 🔄 Restarting container {container.id}...")
        stop_containers()
        container.start()
        container.reload()
    port_mappings = container.attrs["NetworkSettings"]["Ports"]
    return port_mappings["5000/tcp"][0]["HostPort"] if "5000/tcp" in port_mappings else None


def stop_containers():
    print(" 🛑 Stopping all running containers...")
    for container in client.containers.list():
        # Check if '5000/tcp' key exists in the Ports dictionary
        ports = container.attrs["NetworkSettings"]["Ports"]
        if '5000/tcp' in ports and ports['5000/tcp'] is not None:
            port_info = ports['5000/tcp'][0]
            if port_info and 6000 <= int(port_info["HostPort"]) <= 6600:
                container.stop()
        else:
            print(f"No '5000/tcp' port mapping found for container {container.id}")



def health_check_routine(job_id, container_id, port):
    print(f" 💊 Starting health check for job {job_id}...")
    container = client.containers.get(container_id)
    start_time = datetime.now()
    while datetime.now() - start_time < timedelta(minutes=4):
        try:
            response = requests.get(f"http://{ssh_host}:{port}/health-check")
            if response.status_code == 200 and response.json().get("status") == "READY":
                jobs[job_id]["status"] = "predicting"
                save_jobs()
                return
        except requests.exceptions.RequestException:
            pass
        time.sleep(0.2)
    container.stop()
    container.remove()
    jobs.pop(job_id, None)
    save_jobs()


@app.post("/jobs/")
async def add_job(image: str):
    print(f" 🚀 Adding job for image {image}...")
    
    # Check if any job is currently running or exists
    if jobs:
        # Option 2: Stop and remove the existing job
        stop_containers()
        jobs.clear()
        save_jobs()

    container = get_container_by_image(image)
    if container:
        port = start_or_restart_container(container, image)
        job_id = str(container.id)
    else:
        stop_containers()
        port = random.randint(6000, 6600)
        container = client.containers.run(image, detach=True, ports={"5000/tcp": port}, device_requests=[docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])])
        job_id = str(container.id)

    jobs[job_id] = {"image": image, "status": "running", "started_at": str(datetime.now()), "port": port}
    save_jobs()

    Thread(target=health_check_routine, args=(job_id, container.id, port), daemon=True).start()
    return {"job_id": job_id}

@app.get("/jobs/")
async def list_jobs():
    return jobs


class PredictionData(BaseModel):
    image: str
    input: dict


@app.post("/predict")
async def predict(
    request: Request, 
    background_tasks: BackgroundTasks, 
    credentials: HTTPAuthorizationCredentials = Security(authenticate),
    prefer: str = Header(None)):
    print(f" 🧠 Received prediction request with preference: {prefer}")
    data = await request.json()
    job_response = await add_job(data["image"])
    job_id = job_response["job_id"]
    returnOpenAPI = data["openapi"] if "openapi" in data else False

    token = request.headers.get("Authorization").split(" ")[1]
    scope = verify_scope(token, data["image"])
    if not scope:
        raise HTTPException(status_code=403, detail="Not Authorized in scope")

     # Initialize current prediction details
    current_prediction.update({
        "image": data["image"],
        "status": "pending",  # Initial status
        "started": str(datetime.now()),
    })

    if prefer == "respond-async":

        webhook_url = "http://192.168.1.62:8000/webhook"
        external_webhook_url = data["webhook"]
        handle_prediction(job_id, data["input"], webhook_url=webhook_url, external_webhook_url=external_webhook_url)
        return {"job_id": job_id, "message": "Prediction in progress. Results will be sent to the webhook URL."}
    print("returnOpenAPI", returnOpenAPI)
    if returnOpenAPI:
        openapi_spec = get_openapi(job_id)
        if openapi_spec:
            return openapi_spec
        else:
            return json.JSONResponse(status_code=500, content={"message": "Failed to retrieve OpenAPI specification."})
    else:
        # Handle synchronous prediction (as before)
        return handle_prediction(job_id, data["input"])


@app.post("/webhook")
async def webhook(request: Request):
    print(" 📡 Received webhook request.")
    # Endpoint to receive prediction results from the model server
    result = await request.json()
    print(" 📡 Prediction result:", result["input"])
    # Process the result as necessary, potentially updating job statuses or notifying other services
    return {"message": "Received prediction result.", "result": result}


@app.get("/predictions/",include_in_schema=False)
async def list_predictions(
    credentials: HTTPAuthorizationCredentials = Security(authenticate),
):
    try:
        with open("../data/predictions.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []



# Simply the root will return our Svelte build
@app.get("/dashboard", response_class=FileResponse)
async def main():
    return "public/index.html"

 # _app/ will return our Svelte build
@app.get("/dashboard/_app/{path}", response_class=FileResponse)
async def main(path):
    return "public/_app/" + path
def handle_prediction(job_id, input, webhook_url=None, external_webhook_url=None):
    print(f" 🧠 Handling prediction for job {job_id}...")
    job = jobs[job_id]
    start_time = datetime.now()
    timeout = timedelta(minutes=3)

    while job["status"] == "running" and datetime.now() - start_time < timeout:
        time.sleep(0.2)
        job = jobs[job_id]

    if job["status"] == "predicting":
        response = make_prediction(job_id, job["port"], input, webhook_url, external_webhook_url)
        return response
    else:
        handle_job_failure(job_id, job["status"])


def get_openapi(job_id):
    """
    Fetch the OpenAPI specification for the server associated with a given job.
    Assumes that the server provides its OpenAPI specification at /openapi.json endpoint.
    """
    job = jobs.get(job_id)
    while job["status"] == "running":
        time.sleep(0.2)
        job = jobs.get(job_id)

    if job and job["status"] == "predicting":
        try:
            port = job["port"]
            response = requests.get(f"http://{ssh_host}:{port}/openapi.json")
            if response.status_code == 200:
                return response.json()  # Return the OpenAPI specification as a Python dictionary
            else:
                print("Failed to retrieve OpenAPI specification: HTTP Status", response.status_code)
        except requests.exceptions.RequestException as e:
            print("Failed to connect to the server to retrieve OpenAPI specification:", str(e))
    else:
        print("Job is not in a predicting state or does not exist.")

    return None  # Return None if the specification could not be retrieved or if the job is not ready



def make_prediction(job_id, port, input, webhook_url=None, external_webhook_url=None):
    print(f" 🧠 Making prediction for job {job_id}...")
    try:
        print("webhook_url", webhook_url)
        print("external_webhook_url", external_webhook_url)
        if webhook_url and external_webhook_url:
            print(f" 📡 Forwarding prediction result to external webhook URL: {external_webhook_url}")
            input["webhook_url"] = external_webhook_url
            header = {
                "Content-Type": "application/json",
                "Prefer": "respond-async"
            }
            payload = {
                "input": input,
                "webhook": external_webhook_url,
                "webhook_events_filter": ["completed"]
            }
            response = requests.post(f"http://{ssh_host}:{port}/predictions", json=payload, headers=header)
            return
        else:
            response = requests.post(f"http://{ssh_host}:{port}/predictions", json={"input": input})
        
        if response.status_code == 200:
            results = response.json()
            if results is None:
                raise ValueError("No data in response")
            if "metrics" in results and "predict_time" in results["metrics"]:
                duration = results["metrics"]["predict_time"]
            else:
                duration = None
            
            current_prediction.update({
                "status": "success",
                "finished": str(datetime.now()),
                "duration": duration
            })
            update_prediction_file()
            return results
        else:
            current_prediction["status"] = "failed"
            update_prediction_file()
            print("response", response)
            return response.json()
    except requests.exceptions.RequestException as e:
        current_prediction["status"] = "failed"
        update_prediction_file()
        print(f" ❌ Prediction failed for job {job_id}.")
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

    

def handle_job_failure(job_id, status):
    print(f" ❌ Job {job_id} failed with status {status}.")
    jobs.pop(job_id, None)
    save_jobs()
    current_prediction["status"] = "failed"
    update_prediction_file()
    detail = "Job failed during execution." if status == "failed" else "Job timed out or failed."
    raise HTTPException(status_code=408, detail=detail)


if __name__ == "__main__":
    import uvicorn
    print(" 🚀 Server running at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
