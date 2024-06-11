import yaml
from dataclasses import dataclass, field
from typing import List

@dataclass
class Token:
    token: str
    name: str
    scope: List[str]

@dataclass
class Config:
    node : str = "localhost"
    tokens: List[Token] = field(default_factory=list)

def load() -> Config:
    with open("../data/config.yaml", "r") as file:
        data = yaml.safe_load(file)
        return data if data else Config()

def save(config: Config):
    with open("../data/config.yaml", "w") as file:
        yaml.dump(config, file)

def addTokenByName(name: str, token: str, scope: List[str]):
    config = load()
    if not token or not name:
        return "Invalid token or name"
    # Check if name already exists
    for entry in config['tokens']:
        if name == entry['name']:
            return "Name already exists"
    # Add new token not - !!python/object:lib.conf.Token
    config["tokens"].append({
        "token": token,
        "name": name,
        "scope": scope
    })
    save(config)
    return "Token added"

def deleteTokenByName(name: str):
    config = load()
    # Check if name exists
    for entry in config['tokens']:
        if name == entry['name']:
            config['tokens'].remove(entry)
            save(config)
            return "Token deleted"
    return "Name not found"

def updateTokenByName(name: str, token: str, scope: List[str]):
    config = load()
    print(config)
    # Check if name exists
    for entry in config['tokens']:
        if name == entry['name']:
            entry['token'] = token
            entry['scope'] = scope
            save(config)
            return "Token updated"
