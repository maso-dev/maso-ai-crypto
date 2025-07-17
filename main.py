from fastapi import FastAPI
import json
from pathlib import Path

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, world!"}

@app.get("/credentials")
def get_credentials():
    key_path = Path("cdp_api_key.json")
    if not key_path.exists():
        return {"error": "cdp_api_key.json not found"}
    with open(key_path) as f:
        creds = json.load(f)
    # Mask the API key for safety
    masked_creds = {k: (v[:4] + "..." if isinstance(v, str) and len(v) > 8 else v) for k, v in creds.items()}
    return masked_creds 
