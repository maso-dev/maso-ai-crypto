# Maso AI Crypto FastAPI Starter

This is a simple FastAPI application to serve as the foundation for a crypto trading agent. It demonstrates how to:
- Set up a FastAPI app
- Load Coinbase API credentials from a local file
- Provide basic endpoints for testing

## Requirements
- Python 3.8+
- [pip](https://pip.pypa.io/en/stable/)

## Setup

1. **Clone the repository**

```bash
git clone <your-repo-url>
cd maso-ai-crypto
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Add your Coinbase API credentials**

Create a file named `cdp_api_key.json` in the project root with your Coinbase API credentials. Example format:

```json
{
  "apiKey": "YOUR_COINBASE_API_KEY",
  "apiSecret": "YOUR_COINBASE_API_SECRET",
  "passphrase": "YOUR_COINBASE_API_PASSPHRASE"
}
```

**Note:** Never share your real API keys publicly.

## Running the App

Start the FastAPI server with Uvicorn:

```bash
uvicorn main:app --reload
```

- The app will be available at: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Endpoints

- `GET /`  
  Returns a simple hello world message.

- `GET /credentials`  
  Loads and returns (masked) Coinbase API credentials from `cdp_api_key.json`. For testing only—do not use in production.

## Next Steps
- Integrate with the Coinbase API for real account and trading functionality.
- Implement agent logic for portfolio management and trading.

## Security
- Keep your `cdp_api_key.json` file safe and never commit it to version control.
- Remove or secure the `/credentials` endpoint before deploying to production.

---

*This project is a proof of concept and not intended for production use without further security and error handling improvements.* 
