from fastapi import APIRouter, HTTPException
from app.services.price_api import get_crypto_price, get_etf_price

router = APIRouter(prefix="/prices", tags=["prices"])

CRYPTO_SYMBOLS = {"BTC", "ETH"}

@router.get("/{asset}")
def get_price(asset: str):
    asset = asset.upper()
    try:
        if asset in CRYPTO_SYMBOLS:
            price = get_crypto_price(asset)
        else:
            price = get_etf_price(asset)
        return {"asset": asset, "price": price}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))