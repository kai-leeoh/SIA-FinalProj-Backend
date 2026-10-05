from fastapi import APIRouter, HTTPException
from app.services.price_api import get_asset_price

router = APIRouter(prefix="/prices", tags=["prices"])

@router.get("/{asset_type}/{asset}")
def get_price(asset_type: str, asset: str):
    try:
        price = get_asset_price(asset_type, asset)
        if price is None:
            raise HTTPException(status_code=404, detail="Price unavailable")
        return {"asset": asset, "price": price}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))