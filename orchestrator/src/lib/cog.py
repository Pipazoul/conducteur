from fastapi import HTTPException
from datetime import datetime, timedelta
import time
import requests

from lib.predictions import Predictions, PredictionStatus
from lib.nodes import NodeState
class Cog:
    def __init__(self, node, prediction: Predictions, container):
        self.node = node
        self.prediction = prediction
        self.container = container
        self.host = node.host
        ports = self.container.attrs["NetworkSettings"]["Ports"]
        self.port = None
        if '5000/tcp' in ports and ports['5000/tcp'] is not None:
            port_info = ports['5000/tcp'][0]
            if port_info:
                self.port = port_info["HostPort"]
    
    def health_check(self):
        start_time = datetime.now()
        while datetime.now() - start_time < timedelta(minutes=4):
            try:
                response = requests.get(f"http://{self.host}:{self.port}/health-check")
                if response.status_code == 200 and response.json().get("status") == "SETUP_FAILED":
                    self.container.stop()
                    self.container.remove()
                    self.node.state = NodeState.available
                    raise HTTPException(status_code=500, detail=f'Cog setup failed with error {response.json().get("setup").get("logs")}')
                if response.status_code == 200 and response.json().get("status") == "READY":
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(0.2)
        self.container.stop()
        
        self.node.state = NodeState.available
        raise HTTPException(status_code=403, detail="The health_check timed out check your container logs for more information")
    def run(self):
        header = {
            "Content-Type": "application/json",
        }
        payload = {
                "input": self.prediction.input
        }
        self.prediction.status = PredictionStatus.running.value
        self.prediction.update()
        response = requests.post(f"http://{self.host}:{self.port}/predictions", json=payload, headers=header)
        if response.status_code == 200:
            results = response.json()
            if "metrics" in results and "predict_time" in results["metrics"]:
                self.prediction.finished = datetime.now()
                self.prediction.duration = results["metrics"]["predict_time"]
                self.prediction.status = PredictionStatus.completed.value
                self.prediction.update()
                self.node.state = NodeState.available.value
            return results
        else:
            self.prediction.finished = datetime.now()
            self.prediction.duration = 0
            self.prediction.status = PredictionStatus.failed
            self.prediction.update()
            self.node.state = NodeState.available.value
            raise HTTPException(status_code=500, detail=f"Error the container returned a {response.status_code}")
        
        