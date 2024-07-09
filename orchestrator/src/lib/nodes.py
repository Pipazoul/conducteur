import lib.conf as conf
config = conf.load()
nodesPath = config["logs"]["nodesPath"]


def initNodeState():
    