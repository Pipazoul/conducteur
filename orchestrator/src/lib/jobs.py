import json
import lib.conf as conf

config = conf.load()
jobsPath = config["logs"]["jobsPath"]

def load():
    try:
        with open(jobsPath, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save(jobs):
    with open(jobsPath, "w") as file:
        json.dump(jobs, file, indent=4)

