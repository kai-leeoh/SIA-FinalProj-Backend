from fastapi import APIRouter
import requests
import os
import time

router = APIRouter(prefix="/search", tags=["search"])

COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY")

_pse_cache = {"data": [], "time": 0.0}


def get_pse_stocks():
    if _pse_cache["data"] and time.time() - _pse_cache["time"] < 86400:
        return _pse_cache["data"]
    try:
        resp = requests.get(
            "https://api.twelvedata.com/stocks",
            params={"country": "Philippines", "apikey": TWELVE_DATA_API_KEY},
            timeout=10,
        )
        resp.raise_for_status()
        data = [
            s for s in resp.json().get("data", [])
            if s.get("mic_code") == "XPHS" and s.get("type") in ("Common Stock", "REIT")
        ]
        _pse_cache["data"] = data
        _pse_cache["time"] = time.time()
        return data
    except requests.exceptions.RequestException:
        return _pse_cache["data"]


@router.get("")
def search_assets(query: str):
    if not query or len(query) < 1:
        return []

    results = []

    # Crypto search via CoinGecko
    try:
        headers = {"x-cg-demo-api-key": COINGECKO_API_KEY} if COINGECKO_API_KEY else {}
        cg_resp = requests.get(
            "https://api.coingecko.com/api/v3/search",
            params={"query": query},
            headers=headers,
            timeout=5,
        )
        cg_resp.raise_for_status()
        for coin in cg_resp.json().get("coins", [])[:5]:
            results.append({
                "value": coin["id"],
                "label": f"{coin['name']} ({coin['symbol'].upper()})",
                "type": "crypto",
            })
    except requests.exceptions.RequestException:
        pass

    # Philippine stocks (PSE)
    q = query.lower()
    pse_matches = [
        s for s in get_pse_stocks()
        if q in s["symbol"].lower() or q in s["name"].lower()
    ]
    pse_matches.sort(key=lambda s: not s["symbol"].lower().startswith(q))
    for s in pse_matches[:5]:
        results.append({
            "value": f"{s['symbol']}.PSE",
            "label": f"{s['name']} ({s['symbol']}, PSE)",
            "type": "stock",
        })

    # Stock/ETF search via Twelve Data
    try:
        td_resp = requests.get(
            "https://api.twelvedata.com/symbol_search",
            params={"symbol": query},
            timeout=5,
        )
        td_resp.raise_for_status()
        for item in td_resp.json().get("data", [])[:5]:
            results.append({
                "value": item["symbol"],
                "label": f"{item['instrument_name']} ({item['symbol']})",
                "type": "etf",
            })
    except requests.exceptions.RequestException:
        pass

    return results