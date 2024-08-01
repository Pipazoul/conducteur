import random
import docker.types

class Docker:
    def __init__(self, client):
        self.client = client
    def stop_containers(self):
        
        for container in self.client.containers.list():
            ports = container.attrs["NetworkSettings"]["Ports"]
            if '5000/tcp' in ports and ports['5000/tcp'] is not None:
                port_info = ports['5000/tcp'][0]
                if port_info and 6000 <= int(port_info["HostPort"]) <= 6600:
                    container.stop()
            else:
                print(f"No '5000/tcp' port mapping found for container {container.id}")

    def start_or_restart_container(self,container):
        if container.status == "exited":
            self.stop_containers()
            self.client.start()
            self.client.reload()
        port_mappings = container.attrs["NetworkSettings"]["Ports"]
        return port_mappings["5000/tcp"][0]["HostPort"] if "5000/tcp" in port_mappings else None
    
    def get_container_by_image(self,image):
        for container in self.client.containers.list(all=True):
            if container.attrs["Config"]["Image"] == image:
                return container
        return None

    def run_container(self,image):
        self.stop_containers()
        port = random.randint(6000, 6600)
        container = self.client.containers.run(image, detach=True, ports={"5000/tcp": port}, device_requests=[docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])])
        return container, port
    
    def get_container(self,container_id):
        return self.client.containers.get(container_id)
