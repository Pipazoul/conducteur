import json
import time
import requests
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from docker import DockerClient
import docker.types
from threading import Thread
from pydantic import BaseModel
import os
import dotenv
import random

dotenv.load_dotenv()

app = FastAPI()
ssh_user = os.getenv('DOCKER_SSH_USER')
ssh_key_path = os.getenv('DOCKER_SSH_KEY_PATH')
ssh_host = os.getenv('DOCKER_SSH_HOST')
client = None

if ssh_host:
    if ssh_key_path:
        print("Using SSH key for remote Docker access.")
        base_url = f"ssh://{ssh_user}@{ssh_host}"
        client = DockerClient(base_url=base_url, use_ssh_client=True)
    else:
        print("SSH credentials or key must be provided for remote Docker access.")
else:
    client = DockerClient(base_url='unix://var/run/docker.sock')

jobs = {}

# # remove jobs.json file if it exists
# try:
#     os.remove("jobs.json")
# except FileNotFoundError:
#     pass

class PredictRequest(BaseModel):
    image: str

def load_jobs():
    try:
        with open("jobs.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_jobs():
    with open("jobs.json", "w") as file:
        json.dump(jobs, file, indent=4)

def health_check_routine(job_id, container_id, port):
    print("Starting health check routine...")
    container = client.containers.get(container_id)
    start_time = datetime.now()
    while datetime.now() - start_time < timedelta(minutes=4):
        try:
            response = requests.get(f"http://{ssh_host}:{port}/health-check")
            if response.status_code == 200:
                #check if status is READY
                status = response.json()['status']

                if status == 'READY':
                    jobs[job_id]['status'] = 'predicting'
                    save_jobs()
                    print("Job is ready for prediction.")
                    return

        except requests.exceptions.RequestException:
            pass
        time.sleep(30)
    container.stop()
    container.remove()
    jobs.pop(job_id, None)
    save_jobs()

def stop_containers():
    # Stop containers that are not using the required image
    for container in client.containers.list():
        port_info = container.attrs['NetworkSettings']['Ports']['5000/tcp']
        if port_info:
            port = port_info[0]['HostPort']
            if 6000 <= int(port) <= 6600:
                container.stop()
                container.remove()
                print(f"Stopped container on port {port}")

@app.post("/jobs/")
async def add_job(image: str):
    print("Adding job...")

    # Check if a container with the same image is already running
    existing_container = None
    port = None
    for container in client.containers.list():
        container_image = container.attrs['Config']['Image']
        print(f"Container image: {container_image}")
        print(f"Image: {image}")
        if container_image == image:
            print("Found existing container")
            print(f"Container image: {container_image}")
            print(f"Image: {image}")
            existing_container = container
            # update the port
            port = container.attrs['NetworkSettings']['Ports']['5000/tcp'][0]['HostPort']

    # If found, use the existing container's settings
    if existing_container:
        job_id = str(existing_container.id)
        print(f"Using existing container: {job_id}")
        jobs[job_id] = {
            'image': image,
            'status': 'running',
            'started_at': str(datetime.now()),
            'port': port
        }
        save_jobs()
    else:
        
        if any(job['status'] == 'running' for job in jobs.values()):
            raise HTTPException(status_code=400, detail="Another job is currently running.")
        
        stop_containers()
        port = random.randint(6000, 6600)
        container = client.containers.run(
            image,
            detach=True,
            ports={'5000/tcp': port},
            device_requests=[docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])]
        )
        job_id = str(container.id)
        jobs[job_id] = {
            'image': image,
            'status': 'running',
            'started_at': str(datetime.now()),
            'port': port
        }
        save_jobs()
    Thread(target=health_check_routine, args=(job_id, container.id, port), daemon=True).start()

    return {"job_id": job_id}

@app.get("/jobs/")
async def list_jobs():
    return jobs

@app.get("/predict/")
@app.get("/predict/")
async def predict(image: str):
    # Add a new job and start the health check
    job_response = await add_job(image)
    job_id = job_response['job_id']
    job = jobs[job_id]

    # Wait until the job status changes from 'running' or until timeout
    start_time = datetime.now()
    timeout = timedelta(minutes=3)
    while job['status'] == 'running' and datetime.now() - start_time < timeout:
        time.sleep(1)
        job = jobs[job_id]
    print("outside while loop")
    print(job)
    # Check if the health check passed and the job is ready for prediction
    if job['status'] == 'predicting':
        port = job['port']
        try:
            # Attempt to get a prediction from the container
            response = requests.post(f"http://{ssh_host}:{port}/predictions")
            if response.status_code == 200:
                # If successful, remove the job and save the jobs state
                jobs.pop(job_id, None)
                save_jobs()
                return response.json()
            else:
                # return the error message
                data = response.json()
                print(data)
                raise HTTPException(status_code=500)
        except requests.exceptions.RequestException as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        # If the job failed or timed out, raise an exception
        jobs.pop(job_id, None)
        save_jobs()
        if job['status'] == 'failed':
            detail = "Job failed during execution."
        else:
            detail = "Job timed out or failed."
        raise HTTPException(status_code=408, detail=detail)

if __name__ == "__main__":
    jobs = load_jobs()
    try:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        print("Shutting down gracefully...")
        client.close()
        print("Cleanup complete, application stopped.")
