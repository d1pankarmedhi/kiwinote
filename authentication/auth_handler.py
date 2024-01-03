import time
from typing import Dict
from dotenv import load_dotenv
import jwt
import os 

load_dotenv()

JWT_SECRET = os.getenv("SECRET")
JWT_ALGORITHM = os.getenv("ALGORITHM")

class AuthHandler:
    def __init__(self) -> None:
        pass
    @staticmethod
    def token_response(token: str):
        return {
            "access_token": token
        }
    @staticmethod
    def signJWT(user_id: str) -> Dict[str, str]:
        payload = {
            "user_id": user_id,
            "expires": time.time() + 600
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

        return AuthHandler.token_response(token)
    @staticmethod
    def decodeJWT(token: str) -> dict:
        try:
            decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return decoded_token if decoded_token["expires"] >= time.time() else None
        except:
            return {}

