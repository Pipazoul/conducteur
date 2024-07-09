import subprocess
import requests
import time
from datetime import datetime, timedelta
import os

def add_ssh_host_key(hostname):
    print(f" 🔑 Adding SSH host key for {hostname}...")
    known_hosts_path = "/root/.ssh/known_hosts"
    subprocess.run(["ssh-keyscan", "-H", hostname], stdout=open(known_hosts_path, "a"))


def createMissingFolders(folders: dict): 
    for folder in folders:
        if not os.path.exists(folder):
            print(f' 📁 Creating missing directory {folder}' )
            os.makedirs(folder, exist_ok=True)    
    print('✅ Done')
