from fastapi import APIRouter
import requests
import os

router = APIRouter(prefix="/search", tags=["search"])

COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")

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