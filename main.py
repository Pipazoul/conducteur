import json
import os
import random
import requests
import time
from datetime import datetime, timedelta
from threading import Thread
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from docker import DockerClient
import docker.types
import dotenv
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi import Header
from fastapi import BackgroundTasks
import subprocess

dotenv.load_dotenv()
app = FastAPI()

# Load environment variables
ssh_user = os.getenv("DOCKER_SSH_USER")
ssh_key_path = "/root/.ssh/id_rsa"
ssh_host = os.getenv("DOCKER_SSH_HOST")




def add_ssh_host_key(hostname):
    print(f" 🔑 Adding SSH host key for {hostname}...")
    # Adds the SSH host key for the given hostname to the known_hosts file
    known_hosts_path = "/root/.ssh/known_hosts"
    subprocess.run(["ssh-keyscan", "-H", hostname], stdout=open(known_hosts_path, "a"))


add_ssh_host_key(ssh_host)

client = DockerClient(base_url=f"ssh://{ssh_user}@{ssh_host}" if ssh_key_path else "unix://var/run/docker.sock")






# Initialize jobs dictionary
jobs = {}



def load_jobs():
    try:
        with open("jobs.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


jobs = load_jobs()


def save_jobs():
    with open("jobs.json", "w") as file:
        json.dump(jobs, file, indent=4)


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
    container = get_container_by_image(image)
    if container:
        port = start_or_restart_container(container, image)
        job_id = str(container.id)
    else:
        if any(job["status"] == "running" for job in jobs.values()):
            raise HTTPException(status_code=400, detail="Another job is currently running.")
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
async def predict(request: Request, background_tasks: BackgroundTasks, prefer: str = Header(None)):
    print(f" 🧠 Received prediction request with preference: {prefer}")
    data = await request.json()
    job_response = await add_job(data["image"])
    job_id = job_response["job_id"]

    if prefer == "respond-async":

        webhook_url = "http://192.168.1.62:8000/webhook"
        external_webhook_url = data["webhook"]
        handle_prediction(job_id, data["input"], webhook_url=webhook_url, external_webhook_url=external_webhook_url)
        return {"job_id": job_id, "message": "Prediction in progress. Results will be sent to the webhook URL."}
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
                "input": input,  # Ensure 'input' is defined elsewhere in your script
                "webhook": external_webhook_url,  # This should be the top-level key in the payload
                "webhook_events_filter": ["completed"]
            }
            
            response = requests.post(f"http://{ssh_host}:{port}/predictions", json=payload, headers=header)
            return
        else:
            response = requests.post(f"http://{ssh_host}:{port}/predictions", json={"input": input})
        if response.status_code == 200:
            jobs.pop(job_id, None)
            save_jobs()
            return response.json()
        else:
            raise HTTPException(status_code=500)
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=str(e))


def handle_job_failure(job_id, status):
    print(f" ❌ Job {job_id} failed with status {status}.")
    jobs.pop(job_id, None)
    save_jobs()
    detail = "Job failed during execution." if status == "failed" else "Job timed out or failed."
    raise HTTPException(status_code=408, detail=detail)


if __name__ == "__main__":
    import uvicorn
    print(" 🚀 Server running at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
