from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer
from lib.config import Config

class Authenticate:
    config = Config()

    @staticmethod
    def extract_token(request: Request):
        return request.headers.get("Authorization").split(" ")[1]
    
    @staticmethod
    def verify_existing_token(token):
        if token:
            for entry in Authenticate.config.tokens:
                if token == entry['token']:
                    return { 'is_authenticated': True, 'token': token }
        raise HTTPException(status_code=403, detail="Not Authorized")

    @staticmethod
    def verify_image_scope(token: str, image: str):
        for entry in Authenticate.config.tokens:
            if token == entry['token']:
                if image in entry['scope'] or "*" in entry['scope']:
                    return True
        raise HTTPException(status_code=403, detail="The image is not within the scope of your token.")
    
    @staticmethod
    def verify_token_admin(token: str):
        config = Authenticate.conf.load()
        for entry in config['tokens']:
            if token == entry['token'] and "*" in entry['scope']:
                return entry['scope']
        raise HTTPException(status_code=403, detail="Not Authorized")
    
