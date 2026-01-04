import os

API_KEY = os.getenv("REMOTE_PC_API_KEY", "nobody@1906")

def verify_key(key: str):
    if key != API_KEY:
        raise PermissionError("Invalid API Key")
