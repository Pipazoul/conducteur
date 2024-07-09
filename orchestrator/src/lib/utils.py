import subprocess
import requests
import time
from datetime import datetime, timedelta
import os
import json

def add_ssh_host_key(hostname):
    print(f" 🔑 Adding SSH host key for {hostname}...")
    known_hosts_path = "/root/.ssh/known_hosts"
    subprocess.run(["ssh-keyscan", "-H", hostname], stdout=open(known_hosts_path, "a"))


def createMissingFiles(folders: dict):
    # create folders "ex ./logs/file.json" and the missing files in it start from 
    # folders is list of "string"
    for filePath in folders:
        dirname = os.path.dirname(filePath)
        if not os.path.exists(dirname):
            print("Creating directory", dirname)
            os.makedirs(dirname)
            
        if not os.path.isfile(filePath):
            # create file and append {}
            with open(filePath, 'w') as f:
                json.dump([], f)
        