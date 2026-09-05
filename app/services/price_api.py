import os
import time
import requests

TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")

_price_cache = {}
CACHE_DURATION = 60  # seconds

def _get_cached_price(symbol: str):
    if symbol in _price_cache:
        cached_price, cached_time = _price_cache[symbol]
        if time.time() - cached_time < CACHE_DURATION:
            return cached_price
    return None

def _set_cached_price(symbol: str, price: float):
    _price_cache[symbol] = (price, time.time())

def get_crypto_price(symbol: str) -> float:
    symbol = symbol.upper()
    cached = _get_cached_price(symbol)
    if cached is not None:
        return cached

    coingecko_ids = {"BTC": "bitcoin", "ETH": "ethereum"}
    coin_id = coingecko_ids.get(symbol)
    if not coin_id:
        raise ValueError(f"Unsupported crypto symbol: {symbol}")

    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": coin_id, "vs_currencies": "usd"}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    price = data[coin_id]["usd"]

    _set_cached_price(symbol, price)
    return price

def get_etf_price(symbol: str) -> float:
    symbol = symbol.upper()
    cached = _get_cached_price(symbol)
    if cached is not None:
        return cached

    url = "https://api.twelvedata.com/price"
    params = {"symbol": symbol, "apikey": TWELVE_DATA_API_KEY}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    if "price" not in data:
        raise ValueError(f"Could not fetch price for {symbol}: {data}")
    price = float(data["price"])

    _set_cached_price(symbol, price)
    return price