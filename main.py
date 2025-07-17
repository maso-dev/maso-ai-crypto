from fastapi import FastAPI, HTTPException
from pathlib import Path
import json
from binance_client import get_binance_client

app = FastAPI()

@app.get("/")
async def get_root_message() -> dict:
    return {"message": "Hello, world!"}

@app.get("/credentials")
async def get_credentials() -> dict:
    key_path = Path("cdp_api_key.json")
    if not key_path.exists():
        raise HTTPException(status_code=404, detail="cdp_api_key.json not found")
    with open(key_path) as f:
        creds = json.load(f)
    masked_creds = {k: (v[:4] + "..." if isinstance(v, str) and len(v) > 8 else v) for k, v in creds.items()}
    return masked_creds

@app.get("/binance/account")
async def get_binance_account() -> dict:
    try:
        client = get_binance_client()
        account_info = client.get_account()
        return account_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
