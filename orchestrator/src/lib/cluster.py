from lib.docker import Docker
from lib.cog import Cog
from lib.nodes import Node, NodeState
from lib.predictions import Predictions
import time
from fastapi import HTTPException

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
            if node.state == NodeState.available.value:
                available = node
                break
        return available
    
    def run_prediction(self, prediction: Predictions):
        node = self.available_node()
        # loop until we find an available node or all nodes are offline
        while True:
            time.sleep(1) # wait a second before trying again
            node = self.available_node()
            if node:
                break
        # container routine
        node.state = NodeState.busy.value
        node.prediction = prediction
        docker = Docker(node.client)
        container = docker.get_container_by_image(prediction.image)
        if not container:
            container = docker.run_container(prediction.image)
        else:
            container = docker.start_or_restart_container(container)
        print("Container running")
        cog = Cog(node, prediction, container)
        health = cog.health_check()
        if health:
            result = cog.run()
            return result
        node.state = NodeState.available.value
    