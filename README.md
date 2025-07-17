# Maso AI Crypto FastAPI Starter (Binance Edition)

This is a simple FastAPI application to serve as the foundation for a crypto trading agent, now using the Binance API.

The self validation process from Coinbase sucks bad.

## Features

- Set up a FastAPI app
- Load Binance API credentials from a local file
- Provide endpoints for testing and retrieving Binance account info

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

3. **Add your Binance API credentials**

Create a file named `cdp_api_key.json` in the project root with your Binance API credentials. Example format:

```json
{
  "apiKey": "YOUR_BINANCE_API_KEY",
  "secretKey": "YOUR_BINANCE_API_SECRET"
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
  Loads and returns (masked) Binance API credentials from `cdp_api_key.json`. For testing only—do not use in production.

- `GET /binance/account`  
  Returns your Binance account information (requires valid API credentials).

## Security

- Keep your `cdp_api_key.json` file safe and never commit it to version control.
- Remove or secure the `/credentials` endpoint before deploying to production.

---

*This project is a proof of concept and not intended for production use without further security and error handling improvements.*

---

## Dependencies

- fastapi
- uvicorn
- python-binance

See [FastAPI documentation](https://fastapi.tiangolo.com/) for more on models, middleware, and route patterns.

See [python-binance documentation](https://python-binance.readthedocs.io/en/latest/) for Binance API usage. 
