import json
import lib.conf as conf

config = conf.load()
jobsPath = config["logs"]["jobsPath"]

def load():
    try:
        with open(jobsPath, "r") as file:
            print("📂 Loading jobs...")
            print(json.load(file))
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save(jobs):
    with open("../data/logs/jobs.json", "w") as file:
        json.dump(jobs, file, indent=4)

