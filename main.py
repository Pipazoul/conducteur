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


dotenv.load_dotenv()
app = FastAPI()

# Load environment variables
ssh_user = os.getenv("DOCKER_SSH_USER")
ssh_key_path = os.getenv("DOCKER_SSH_KEY_PATH")
ssh_host = os.getenv("DOCKER_SSH_HOST")
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
        stop_containers()
        container.start()
        container.reload()
    port_mappings = container.attrs["NetworkSettings"]["Ports"]
    return port_mappings["5000/tcp"][0]["HostPort"] if "5000/tcp" in port_mappings else None


def stop_containers():
    for container in client.containers.list():
        port_info = container.attrs["NetworkSettings"]["Ports"]["5000/tcp"]
        if port_info:
            port = port_info[0]["HostPort"]
            if 6000 <= int(port) <= 6600:
                container.stop()


def health_check_routine(job_id, container_id, port):
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
async def predict(request: Request):
    data = await request.json()
    job_response = await add_job(data["image"])
    job_id = job_response["job_id"]
    return await handle_prediction(job_id, data["input"])


async def handle_prediction(job_id, input):
    job = jobs[job_id]
    start_time = datetime.now()
    timeout = timedelta(minutes=3)

    while job["status"] == "running" and datetime.now() - start_time < timeout:
        time.sleep(0.2)
        job = jobs[job_id]

    if job["status"] == "predicting":
        response = await make_prediction(job_id, job["port"], input)
        return response
    else:
        handle_job_failure(job_id, job["status"])


async def make_prediction(job_id, port, input):
    try:
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
    jobs.pop(job_id, None)
    save_jobs()
    detail = "Job failed during execution." if status == "failed" else "Job timed out or failed."
    raise HTTPException(status_code=408, detail=detail)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
