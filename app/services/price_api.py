import os
import time
import requests

TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")

_price_cache = {}
CACHE_DURATION = 60

def _get_cached_price(key: str):
    if key in _price_cache:
        cached_price, cached_time = _price_cache[key]
        if time.time() - cached_time < CACHE_DURATION:
            return cached_price
    return None

def _set_cached_price(key: str, price: float):
    _price_cache[key] = (price, time.time())

def get_crypto_price(coingecko_id: str) -> float | None:
    coingecko_id = coingecko_id.lower()
    cached = _get_cached_price(coingecko_id)
    if cached is not None:
        return cached

    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": coingecko_id, "vs_currencies": "usd"}
    headers = {"x-cg-demo-api-key": COINGECKO_API_KEY} if COINGECKO_API_KEY else {}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        if coingecko_id not in data:
            return None
        price = data[coingecko_id]["usd"]
        _set_cached_price(coingecko_id, price)
        return price
    except requests.exceptions.RequestException:
        return None

def get_etf_price(symbol: str) -> float | None:
    symbol = symbol.upper()
    cached = _get_cached_price(symbol)
    if cached is not None:
        return cached

    url = "https://api.twelvedata.com/price"
    params = {"symbol": symbol, "apikey": TWELVE_DATA_API_KEY}

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        if "price" not in data:
            return None
        price = float(data["price"])
        _set_cached_price(symbol, price)
        return price
    except requests.exceptions.RequestException:
        return None