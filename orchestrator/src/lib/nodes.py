import lib.conf as conf
import json
import lib.docker as docker
config = conf.load()
nodesPath = config["logs"]["nodesPath"]


def state() -> dict:
    with open(nodesPath, 'r') as file:
        return json.load(file)
    
def initNodeState():
    nodes = config["nodes"]
    nodesState = []
    for node in nodes:
        # clear the node state file and append []
        with open(nodesPath, 'w') as outfile:
            json.dump([], outfile)
        try:
            docker.connectToDockerClient(node)
            nodeState = { "name": node["name"],"host": node["host"] ,"user": node["user"], "state": "available", "weight": node["weight"], "rsa": node["rsa"]}
        except Exception as e:
            print("Failed to connect to docker on "+ node["host"] +" with error : ",e)
            # Update the state of this node to unavailable
            nodeState = { "name": node["name"],"host": node["host"] ,"user": node["user"], "state": "offline", "weight": node["weight"], "rsa": node["rsa"]}
        nodesState.append(nodeState)
    with open(nodesPath, 'w') as outfile:
        json.dump(nodesState, outfile)


def getAvailableNode() -> dict:
    nodes = state()
    for node in nodes:
        try:
            docker.connectToDockerClient(node)
        except Exception as e:
            print("Failed to connect to docker on "+ node["host"] +" with error : ",e)
            # Update the state of this node to unavailable
            node["state"] = "offline"
    
    # Find the most heavy available node
    available_nodes = [n for n in nodes if n["state"]  == "available"]
    if available_nodes:
        max_weight_node = max(available_nodes, key=lambda k: k['weight'])
        return max_weight_node
    else:
        # Handle the case where there are no available nodes
        return None

def updateState(name, nodeState):
    nodes = state()
    for node in nodes:
        if node["name"] == name:
            node["state"] = nodeState
    
    with open(nodesPath, 'w') as outfile:
        json.dump(nodes, outfile)