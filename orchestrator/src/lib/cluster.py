from lib.docker import Docker
from lib.cog import Cog
from lib.nodes import Node, NodeState
from lib.predictions import Predictions
from lib.co2 import Co2
import time
from datetime import datetime, timedelta
from fastapi import HTTPException
import threading
import os
TIMEOUT = float(os.getenv('TIMEOUT', '1'))  # minutes

class Cluster:
    def __init__(self, nodes, monitor_port=4560, carbon_intensity=100):
        self.lock = threading.Lock()
        self.nodes = [Node(name=n['name'], user=n['user'], host=n['host'], rsa=n['rsa'], weight=n['weight']) for n in nodes]
        for node in self.nodes:
            node.connect()
            # setup co2 monitor for that node
            print("Pulling c02 monitor container, it can take a while...")
            co2 = self.setup_monitor_container(node, port=monitor_port, carbon_intensity=carbon_intensity)
            node.co2 = co2
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

    def setup_container(self, node, image, port=None):
        with self.lock:
            print("Setting up a new container on node", node.name, "for image", image)
            docker = Docker(node.client)
            print('Check if image exists in the node')
            container = docker.get_container_by_image(image)
            if not container:
                print('Image not found on the node run pull')
                if not port:
                    container = docker.run_container(image)
                else:
                    container = docker.run_container(image, port=port)
            else:
                print('Image found on the node run start')
                container = docker.start_or_restart_container(container)
            return container
    
    def setup_monitor_container(self, node, port, carbon_intensity):
        image = "yassinsiouda/cog-gpu-monitor:latest"
        container =  self.setup_container(node, image, port)
    
        if isinstance(container, Exception):
            node.state = NodeState.available.value
            raise container
        prediction = Predictions(
            image = image,
            user="monitor",
            node= node.name,
            started=datetime.now(),
            input= {}
        )
        cog = Cog(node, prediction, container)
        health = cog.health_check()
        if health:
            return Co2(cog,carbon_intensity)
        raise HTTPException(status_code=503, detail="Failed to set up monitor container")

    

    def queue_prediction(self, prediction: Predictions):
        print("Queueing prediction...")
        image = prediction.image
        # wait for a available node
        node = self.wait_node()
        node.state = NodeState.busy.value
        # setup the docker container on that node and get it ready for use
        container = self.setup_container(node, image)
        
        # check is is string
        if isinstance(container, Exception):
            node.state = NodeState.available.value
            raise container
        # create a new Cog (container object) and run the prediction on it
        cog = Cog(node, prediction, container)
        health = cog.health_check()
        if health:
            node.co2.start()
            result = cog.run()
            node.co2.stop()
            node.state = NodeState.available.value
            prediction.co2 = node.co2.grams_emitted
            print("CO2 emitted by prediction: ", node.co2.grams_emitted, " grams")
            prediction.node = node.name
            prediction.update()
            result["co2"] = prediction.co2
            return result
    
    def queue_openai_spec(self, image: str):
        print("Queueing openai spec...")
        # wait for a available node
        node = self.wait_node()
        print("Node selected", node.name)
        node.state = NodeState.busy.value
        # setup the docker container on that node and get it ready for use
        container = self.setup_container(node, image)
        if isinstance(container, Exception):
            node.state = NodeState.available.value
            raise container

        print("Container setup", container)
        cog = Cog(node, {}, container)
        print("Cog created")
        health = cog.health_check()
        print(f"Health check {health}")
        if health:
            result = cog.get_openapi_specs()
            return result
        node.state = NodeState.available.value

    
    def global_status(self):
        # Initialize variables
        status = NodeState.unknown.value
        all_busy = True
        
        # Iterate over each node in the cluster
        for node in self.nodes:
            if node.state == NodeState.available.value:
                status = NodeState.available.value
                all_busy = False
                break  # Stop iterating if we find an available node
            elif node.state == NodeState.busy.value:
                continue  # Skip to the next iteration if a node is busy
            else:
                status = NodeState.offline.value
        
        # If all nodes are busy, set the global status to busy
        if all_busy:
            status = NodeState.busy.value
        
        return status