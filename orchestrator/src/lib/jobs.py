import json


def load():
    try:
        with open("../data/jobs.json", "r") as file:
            print("📂 Loading jobs...")
            print(json.load(file))
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save(jobs):
    with open("../data/jobs.json", "w") as file:
        json.dump(jobs, file, indent=4)


class JobsHandler:
    def __init__(self):
        self.jobs = load()

    def load(self):
        return self.jobs

    def save(self):
        save(self.jobs)
