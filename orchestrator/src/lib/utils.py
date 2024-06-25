import subprocess
import requests
import time
from datetime import datetime, timedelta
from jobs import jobsHandler 


def add_ssh_host_key(hostname):
    print(f" 🔑 Adding SSH host key for {hostname}...")
    known_hosts_path = "/root/.ssh/known_hosts"
    subprocess.run(["ssh-keyscan", "-H", hostname], stdout=open(known_hosts_path, "a"))


def health_check_routine(job_id, container_id, port, ssh_host):
    print(f" 💊 Starting health check for job {job_id}...")
    from .docker import get_container
    container = get_container(container_id)
    start_time = datetime.now()
    while datetime.now() - start_time < timedelta(minutes=4):
        try:
            response = requests.get(f"http://{ssh_host}:{port}/health-check")
            if response.status_code == 200 and response.json().get("status") == "READY":
                jobs = jobsHandler.load()
                jobs[job_id]["status"] = "predicting"
                jobsHandler.save(jobs)
                return
        except requests.exceptions.RequestException:
            pass
        time.sleep(0.2)
    container.stop()
    container.remove()
    jobs.pop(job_id, None)
    jobsHandler.save(jobs)