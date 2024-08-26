import threading
from docker import DockerClient
import subprocess
from enum import Enum
from lib.predictions import Predictions
import logging

class NodeState(Enum):
    unknown = "unknown"
    available = "available"
    offline = "offline"
    busy = "busy"

class Node:
    def __init__(self, name, user, host, rsa, weight, co2=None,client=None):
        logging.debug("🔵 Creating node %s", name)
        self.lock = threading.Lock()
        self.name = name
        self.user = user
        self.host = host
        self.rsa = rsa
        self.weight = weight
        self.client = client
        self.state = NodeState.unknown.value
        self.prediction: Predictions = None
        self.co2 = co2
    def add_ssh_host_key(self,host):
        logging.info("🔵 Adding ssh host key for %s", host)
        known_hosts_path = "/root/.ssh/known_hosts"
        subprocess.run(["ssh-keyscan", "-H", host], stdout=open(known_hosts_path, "a"))
    
    def ping(self):
        logging.debug("🔵 Pinging node %s", self.name)
        # true if pingable, false otherwise
        does_ping = subprocess.call(['ping', '-c', '1', self.host], stdout=subprocess.PIPE) == 0
        self.state = NodeState.available.value if does_ping else NodeState.offline.value
        return does_ping

    def connect(self):
        logging.debug("🔵 Connecting to node %s", self.name)
        with self.lock:
            self.add_ssh_host_key(self.host)
            self.client = DockerClient(base_url=f"ssh://{self.user}@{self.host}" if self.rsa else "unix://var/run/docker.sock")
            self.state = NodeState.available.value if self.client else NodeState.offline.value

    def disconnect(self):
        logging.debug("🔵 Disconnecting from node %s", self.name)
        with self.lock:
            self.client.close()
            self.state = NodeState.offline.value


