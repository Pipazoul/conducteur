from fastapi import HTTPException, Request
from lib.config import Config
import logging

class Authenticate:
    config = Config()

    @staticmethod
    def extract_token(request: Request):
        logging.debug("🔑 Extracting Token from Request Header")
        return request.headers.get("Authorization").split(" ")[1]
    
    @staticmethod
    def verify_existing_token(token):
        if token:
            for entry in Authenticate.config.tokens:
                if token == entry['token']:
                    return { 'is_authenticated': True, 'token': token }
        logging.debug("🔑 Token does not exist")
        raise HTTPException(status_code=403, detail="Not Authorized")

    @staticmethod
    def verify_image_scope(token: str, image: str):
        logging.debug("🔑 Verifying Image Scope")
        for entry in Authenticate.config.tokens:
            if token == entry['token']:
                if image in entry['scope'] or "*" in entry['scope']:
                    return True
        raise HTTPException(status_code=403, detail="The image is not within the scope of your token.")
    
    @staticmethod
    def verify_token_admin(token: str):
        logging.debug("🔑 Verifying Admin Token")
        for entry in Authenticate.config.tokens:
            if token == entry['token'] and "*" in entry['scope']:
                return entry['scope']
        raise HTTPException(status_code=403, detail="Not Authorized")
    
    def verify_token_user(token: str, name: str):
        logging.debug("🔑 Verifying User Token")
        for entry in Authenticate.config.tokens:
            if token == entry['token'] and name == entry['name'] or "*" in entry['scope']:
                return True
        raise HTTPException(status_code=403, detail="Not Authorized")
    @staticmethod
    def get_all_tokens():
        logging.debug("🔑 Getting all tokens")
        return Authenticate.config.tokens
    
    @staticmethod
    def get_all_users():
        logging.debug("🔑 Getting all users")
        users = []
        for entry in Authenticate.config.tokens:
            user = entry['name']
            users.append(user)
        return users
    @staticmethod
    def get_user(token):
        logging.debug("🔑 Getting user")
        for entry in Authenticate.config.tokens:
            if token == entry['token']:
                return entry
            