import random
import docker.types
from fastapi import HTTPException
import os
import time


class Docker:
    def __init__(self, client):
        self.client = client
    def stop_containers(self):
        print("Stopping containers")
        for container in self.client.containers.list():
            ports = container.attrs["NetworkSettings"]["Ports"]
            if '5000/tcp' in ports and ports['5000/tcp'] is not None:
                port_info = ports['5000/tcp'][0]
                if port_info and 6000 <= int(port_info["HostPort"]) <= 6600:
                    container.stop()
            else:
                return

    def start_or_restart_container(self,container):
        print("Starting or restarting containers")
        if container.status == "exited":
            self.stop_containers()
            container.start()
            container.reload()
        return container
    
    def get_container_by_image(self,image):
        print("Getting containers by image")
        for container in self.client.containers.list(all=True):
            if container.attrs["Config"]["Image"] == image:
                return container
        return None

    def run_container(self, image, timeout=30, port=None):
        print("Running containers")
        self.stop_containers()
        if not port:
            port = random.randint(6000, 6600)
        try:
            print("Running image", image)
            container = self.client.containers.run(
                image, detach=True, ports={"5000/tcp": port}, 
                device_requests=[docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])])

            start_time = time.time()
            print("container", container.status)
            while container.status != 'running':
                if time.time() - start_time > timeout:
                    return HTTPException(
                        status_code=403, 
                        detail=f'Timeout: Container {container.id} did not start within {timeout} seconds', 
                    )
                
                print(f'Waiting for container {container.id} to start...')
                time.sleep(1)
                container.reload()

            return container

        except(docker.errors.APIError) as e:
            if 'NAME_UNKNOWN' in str(e):
                return HTTPException(
                    status_code=404, 
                    detail="The Docker image you are trying to run does not exist.", 
                )
            else:
                return HTTPException(
                    status_code=403, 
                    detail="Could not run the Docker image due to "+str(e), 
                )

    
    def get_container(self,container_id):
        print("Getting containers")
        return self.client.containers.get(container_id)
