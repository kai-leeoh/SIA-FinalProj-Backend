from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models import Holding, HoldingCreate, User
from app.dependencies import get_current_user
from app.services.price_api import get_crypto_price, get_etf_price

router = APIRouter(prefix="/holdings", tags=["holdings"])

@router.get("")
def get_holdings(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return session.exec(select(Holding).where(Holding.user_id == current_user.id)).all()

@router.get("/enriched")
def get_enriched_holdings(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    holdings = session.exec(select(Holding).where(Holding.user_id == current_user.id)).all()
    result = []
    for h in holdings:
        try:
            price = get_crypto_price(h.asset) if h.type == "crypto" else get_etf_price(h.asset)
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
def create_holding(
    holding: HoldingCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    db_holding = Holding(**holding.dict(), user_id=current_user.id)
    session.add(db_holding)
    session.commit()
    session.refresh(db_holding)
    return db_holding

@router.put("/{holding_id}")
def update_holding(
    holding_id: int,
    updated: HoldingCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    holding = session.get(Holding, holding_id)
    if not holding or holding.user_id != current_user.id:
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
def delete_holding(
    holding_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    holding = session.get(Holding, holding_id)
    if not holding or holding.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Holding not found")
    session.delete(holding)
    session.commit()