import requests
from pathlib import Path
from dotenv import dotenv_values

env_path = Path(__file__).resolve().parent.parent.parent / ".env"
config = dotenv_values(env_path)

TWELVE_DATA_API_KEY = config.get("TWELVE_DATA_API_KEY")

def get_crypto_price(symbol: str) -> float:
    coingecko_ids = {"BTC": "bitcoin", "ETH": "ethereum"}
    coin_id = coingecko_ids.get(symbol.upper())
    if not coin_id:
        raise ValueError(f"Unsupported crypto symbol: {symbol}")

    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": coin_id, "vs_currencies": "usd"}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    return data[coin_id]["usd"]

def get_etf_price(symbol: str) -> float:
    url = "https://api.twelvedata.com/price"
    params = {"symbol": symbol.upper(), "apikey": TWELVE_DATA_API_KEY}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    if "price" not in data:
        raise ValueError(f"Could not fetch price for {symbol}: {data}")
    return float(data["price"])