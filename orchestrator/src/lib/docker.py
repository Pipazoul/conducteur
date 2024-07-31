import os
import random
from datetime import datetime
from docker import DockerClient
import docker.types
import lib.utils as utils

# # Load environment variables
# ssh_user = os.getenv("DOCKER_SSH_USER")
# ssh_key_path = "/root/.ssh/id_rsa"
# ssh_host = os.getenv("DOCKER_SSH_HOST")

# utils.add_ssh_host_key(ssh_host)
# client = DockerClient(base_url=f"ssh://{ssh_user}@{ssh_host}" if ssh_key_path else "unix://var/run/docker.sock")

# Somewhere in the global scope
docker_clients = {}

def connectToDockerClient(node):
    # Check if client already exists and is connected
    if node['host'] in docker_clients and docker_clients[node['host']].ping():
        return docker_clients[node['host']]

    # Create a new client and store in the dictionary
    utils.add_ssh_host_key(node['host'])
    client = DockerClient(base_url=f"ssh://{node['user']}@{node['host']}" if node['rsa'] else "unix://var/run/docker.sock")
    docker_clients[node['host']] = client
    
    return client

def stop_containers(node):
    client = connectToDockerClient(node)
    for container in client.containers.list():
        ports = container.attrs["NetworkSettings"]["Ports"]
        if '5000/tcp' in ports and ports['5000/tcp'] is not None:
            port_info = ports['5000/tcp'][0]
            if port_info and 6000 <= int(port_info["HostPort"]) <= 6600:
                container.stop()
        else:
            print(f"No '5000/tcp' port mapping found for container {container.id}")

def start_or_restart_container(node,container):
    client = connectToDockerClient(node)
    if container.status == "exited":
        stop_containers(node)
        container.start()
        container.reload()
    port_mappings = container.attrs["NetworkSettings"]["Ports"]
    return port_mappings["5000/tcp"][0]["HostPort"] if "5000/tcp" in port_mappings else None

def get_container_by_image(node,image):
    client = connectToDockerClient(node)
    for container in client.containers.list(all=True):
        if container.attrs["Config"]["Image"] == image:
            return container
    return None

def run_container(node,image):
    client = connectToDockerClient(node)
    stop_containers(node)
    port = random.randint(6000, 6600)
    container = client.containers.run(image, detach=True, ports={"5000/tcp": port}, device_requests=[docker.types.DeviceRequest(count=-1, capabilities=[["gpu"]])])
    return container, port

def get_container(node,container_id):
    client = connectToDockerClient(node)
    return client.containers.get(container_id)
