from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import Holding
from app.services.price_api import get_crypto_price, get_etf_price

router = APIRouter(prefix="/holdings", tags=["holdings"])

CRYPTO_SYMBOLS = {"BTC", "ETH"}

@router.get("")
def get_holdings(session: Session = Depends(get_session)):
    return session.exec(select(Holding)).all()

@router.get("/enriched")
def get_enriched_holdings(session: Session = Depends(get_session)):
    holdings = session.exec(select(Holding)).all()
    result = []
    for h in holdings:
        try:
            price = get_crypto_price(h.asset) if h.asset in CRYPTO_SYMBOLS else get_etf_price(h.asset)
        except Exception:
            price = None

        current_value = price * h.quantity if price is not None else None
        gain_loss = current_value - h.cost_basis if current_value is not None else None

        result.append({
            "id": h.id,
            "asset": h.asset,
            "type": h.type,
            "quantity": h.quantity,
            "cost_basis": h.cost_basis,
            "current_price": price,
            "current_value": current_value,
            "gain_loss": gain_loss,
        })
    return result

@router.post("", status_code=201)
def create_holding(holding: Holding, session: Session = Depends(get_session)):
    session.add(holding)
    session.commit()
    session.refresh(holding)
    return holding

@router.put("/{holding_id}")
def update_holding(holding_id: int, updated: Holding, session: Session = Depends(get_session)):
    holding = session.get(Holding, holding_id)
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    holding.asset = updated.asset
    holding.type = updated.type
    holding.quantity = updated.quantity
    holding.cost_basis = updated.cost_basis
    session.add(holding)
    session.commit()
    session.refresh(holding)
    return holding

@router.delete("/{holding_id}", status_code=204)
def delete_holding(holding_id: int, session: Session = Depends(get_session)):
    holding = session.get(Holding, holding_id)
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    session.delete(holding)
    session.commit()