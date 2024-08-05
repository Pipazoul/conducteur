from lib.docker import Docker
from lib.cog import Cog
from lib.nodes import Node, NodeState
from lib.predictions import Predictions
import time
from datetime import datetime, timedelta
from fastapi import HTTPException
import threading
import os
TIMEOUT = float(os.getenv('TIMEOUT', '1'))  # minutes

class Cluster:
    def __init__(self, nodes):
        self.lock = threading.Lock()
        self.nodes = [Node(name=n['name'], user=n['user'], host=n['host'], rsa=n['rsa'], weight=n['weight']) for n in nodes]
        for node in self.nodes:
            node.connect()
    
    def disconnect_all(self):
        for node in self.nodes:
            node.disconnect()
    
    def select_node(self):
        print('Selecting node...')
        available = None
        # sort nodes by weight by the uppest and return the first one that is available
        self.nodes = sorted(self.nodes, key=lambda n: n.weight, reverse=True)
        print('Nodes sorted by weight: {}'.format([n.name for n in self.nodes]))
        for node in self.nodes:
            print('Checking node {}'.format(node.name))
            if node.state == NodeState.available.value:
                print('Node {} selected'.format(node.name))
                available = node
                break
        return available


    def wait_node(self):
        with self.lock:
            print("Waiting for a available node...")
            start_time = datetime.now()
            while datetime.now() - start_time < timedelta(minutes=TIMEOUT):
                print("Waiting for a available node...")
                time.sleep(1) # wait a second before trying again
                node = self.select_node()
                if node:
                    return node
            raise HTTPException(status_code=503, detail="No available nodes")

    def setup_container(self, node, image):
        with self.lock:
            print("Setting up a new container on node", node.name, "for image", image)
            docker = Docker(node.client)
            container = docker.get_container_by_image(image)
            if not container:
                container = docker.run_container(image)
            else:
                container = docker.start_or_restart_container(container)
            return container
    
    def queue_prediction(self, prediction: Predictions):
        print("Queueing prediction...")
        image = prediction.image
        # wait for a available node
        node = self.wait_node()
        node.state = NodeState.busy.value
        # setup the docker container on that node and get it ready for use
        container = self.setup_container(node, image)
        # create a new Cog (container object) and run the prediction on it
        cog = Cog(node, prediction, container)
        health = cog.health_check()
        if health:
            result = cog.run()
            return result
        node.state = NodeState.available.value
    
    def queue_openai_spec(self, image: str):
        print("Queueing openai spec...")
        # wait for a available node
        node = self.wait_node()
        node.state = NodeState.busy.value
        # setup the docker container on that node and get it ready for use
        container = self.setup_container(node, image)
        cog = Cog(node, {}, container)
        health = cog.health_check()
        if health:
            result = cog.get_openapi_specs()
            return result
        node.state = NodeState.available.value
    