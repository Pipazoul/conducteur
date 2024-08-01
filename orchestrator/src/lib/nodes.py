from docker import DockerClient
import subprocess
from enum import Enum
from lib.predictions import Predictions
from lib.docker import Docker
import time

class NodeState(Enum):
    unknown = "unknown"
    available = "available"
    offline = "offline"
    busy = "busy"

class Node:
    def __init__(self, name, user, host, rsa, weight, client=None):
        self.name = name
        self.user = user
        self.host = host
        self.rsa = rsa
        self.weight = weight
        self.client = client
        self.state = NodeState.unknown
        self.prediction: Predictions = None
    def add_ssh_host_key(self,host):
        known_hosts_path = "/root/.ssh/known_hosts"
        subprocess.run(["ssh-keyscan", "-H", host], stdout=open(known_hosts_path, "a"))
    
    def ping(self):
        # true if pingable, false otherwise
        does_ping = subprocess.call(['ping', '-c', '1', self.host], stdout=subprocess.PIPE) == 0
        self.state = NodeState.available if does_ping else NodeState.offline
        return does_ping

    def connect(self):
        self.add_ssh_host_key(self.host)
        self.client = DockerClient(base_url=f"ssh://{self.user}@{self.host}" if self.rsa else "unix://var/run/docker.sock")
        self.state = NodeState.available if self.client else NodeState.offline

    def disconnect(self):
        self.client.close()
        self.state = NodeState.offline



class Cluster:
    def __init__(self, nodes):
        self.nodes = [Node(name=n['name'], user=n['user'], host=n['host'], rsa=n['rsa'], weight=n['weight']) for n in nodes]
        for node in self.nodes:
            node.connect()
    
    def disconnect_all(self):
        for node in self.nodes:
            node.disconnect()
    
    def available_node(self):
        available = None
        # sort nodes by weight by the uppest and return the first one that is available
        self.nodes = sorted(self.nodes, key=lambda n: n.weight, reverse=True)

        for node in self.nodes:
            if node.state == NodeState.available:
                available = node
                break
        return available
    
    def run_prediction(self, prediction: Predictions):
        node = self.available_node()
        # loop until we find an available node or all nodes are offline
        while not node and any(n.state == NodeState.available for n in self.nodes):
            time.sleep(1) # wait a second before trying again
            node = self.available_node()
            
        if node:
            print("Running prediction on", node.name)
            # container routine
            node.prediction = prediction
            docker = Docker(node.client)
            container = docker.get_container_by_image(prediction.image)
            if not container:
                print("Creating new container for", prediction.image)
                container = docker.run_container(prediction.image)
            else:
                container = docker.start_or_restart_container(container)
  
        