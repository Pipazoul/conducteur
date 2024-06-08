import subprocess

def add_ssh_host_key(hostname):
    print(f" 🔑 Adding SSH host key for {hostname}...")
    known_hosts_path = "/root/.ssh/known_hosts"
    subprocess.run(["ssh-keyscan", "-H", hostname], stdout=open(known_hosts_path, "a"))
