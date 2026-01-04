import os

API_KEY = os.getenv("REMOTE_PC_API_KEY", "default_key")

def verify_key(key: str):
    if key != API_KEY:
        raise PermissionError("Invalid API Key")
