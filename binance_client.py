from binance.client import Client
from pathlib import Path
import json

def get_binance_client() -> Client:
    CDP_KEY_FILE = Path("cdp_api_key.json")
    if not CDP_KEY_FILE.exists():
        raise FileNotFoundError("cdp_api_key.json not found")
    with open(CDP_KEY_FILE) as f:
        creds = json.load(f)
    api_key = creds.get("apiKey")
    api_secret = creds.get("secretKey")
    if not api_key or not api_secret:
        raise ValueError("API key or secret missing in cdp_api_key.json")
    return Client(api_key, api_secret) 
