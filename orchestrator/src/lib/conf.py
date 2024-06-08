import yaml

class Token:
    token: str
    name: str
    scope: list

class Config:
    tokens: list[Token]

def load() -> Config:
    with open("../data/config.yaml", "r") as file:
        return yaml.safe_load(file)

def addTokenByName(name: str, token: str, scope: list[str]):
    config = load()
    # Check if name already exists
    for entry in config.tokens:
        if name == entry.name:
            return "Name already exists"
    # Add new token
    config.tokens.append(Token(token=token, name=name, scope=scope))
    with open("../../data/config.yaml", "w") as file:
        yaml.safe_dump(config, file)
    return "Token added"

def deleteTokenByName(name: str):
    config = load()
    # Check if name exists
    for entry in config.tokens:
        if name == entry.name:
            config.tokens.remove(entry)
            with open("../../data/config.yaml", "w") as file:
                yaml.safe_dump(config, file)
            return "Token deleted"
    return "Name not found"

def updateTokenByName(name: str, token: str, scope: list[str]):
    config = load()
    # Check if name exists
    for entry in config.tokens:
        if name == entry.name:
            entry.token = token
            entry.scope = scope
            with open("../../data/config.yaml", "w") as file:
                yaml.safe_dump(config, file)
            return "Token updated"
    return "Name not found"
    

