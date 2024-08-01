import yaml
class Config:
    def __init__(self):
        self.nodes = []
        self.tokens = []
        with open("/app/data/config.yaml") as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            for node in data['nodes']:
                self.nodes.append(node)
            for token in data['tokens']:
                self.tokens.append(token)
            