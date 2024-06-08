import json


def load():
    try:
        with open("../data/jobs.json", "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save(jobs):
    with open("../data/jobs.json", "w") as file:
        json.dump(jobs, file, indent=4)
