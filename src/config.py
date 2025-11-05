import os
from dotenv import load_dotenv

load_dotenv()

def get_x_bearer_token():
    token = os.getenv("X_BEARER_TOKEN")
    if not token:
        raise RuntimeError("X_BEARER_TOKEN tidak ditemukan di .env")
    return token
