import os
import time
import requests

TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")

_price_cache = {}
CACHE_DURATION = 60

def _get_cached_price(key: str, ttl: int = CACHE_DURATION):
    if key in _price_cache:
        cached_price, cached_time = _price_cache[key]
        if time.time() - cached_time < ttl:
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

def get_php_to_usd() -> float | None:
    cached = _get_cached_price("FX:PHPUSD", ttl=3600)
    if cached is not None:
        return cached
    try:
        response = requests.get(
            "https://api.frankfurter.dev/v1/latest",
            params={"base": "PHP", "symbols": "USD"},
            timeout=5,
        )
        response.raise_for_status()
        rate = response.json()["rates"]["USD"]
        _set_cached_price("FX:PHPUSD", rate)
        return rate
    except (requests.exceptions.RequestException, KeyError):
        return None


def _get_pse_price_php(symbol: str) -> float | None:
    try:
        import yfinance as yf
        price = yf.Ticker(f"{symbol}.PS").fast_info["last_price"]
        if price:
            return float(price)
    except Exception as e:
        print("yfinance PSE error:", e)
    return None


def get_pse_price(asset: str) -> float | None:
    symbol = asset.upper().removesuffix(".PSE")
    key = f"PSE:{symbol}"
    cached = _get_cached_price(key)
    if cached is not None:
        return cached

    php_price = _get_pse_price_php(symbol)
    if php_price is None:
        return None

    rate = get_php_to_usd()
    if rate is None:
        return None

    usd_price = php_price * rate
    _set_cached_price(key, usd_price)
    return usd_price


def get_asset_price(asset_type: str, asset: str) -> float | None:
    if asset_type == "crypto":
        return get_crypto_price(asset)
    if asset_type == "stock":
        return get_pse_price(asset)
    return get_etf_price(asset)