from binance.client import Client
from pathlib import Path
import os

def get_binance_client() -> Client:
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        raise ValueError("API key or secret missing in environment variables")

    
    return Client(api_key, api_secret) 
