import yaml
import logging
class Config:
    def __init__(self):
        logging.debug("📝 Loading config")
        self.nodes = []
        self.tokens = []
        with open("/app/data/config.yaml") as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            for node in data['nodes']:
                self.nodes.append(node)
            for token in data['tokens']:
                self.tokens.append(token)
            self.co2 = {
                'port': data['co2'][0]['port'],
                'carbon_intensity': data['co2'][1]['carbon_intensity']
            }
    def get_user_by_token(self, token):
        logging.debug("📝 Getting user by token" + str(token))
        for tk in self.tokens:
            if tk["token"] == token:
                return tk["name"]
        return None