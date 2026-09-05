from typing import Optional
from sqlmodel import SQLModel, Field

class Holding(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    asset: str
    type: str
    quantity: float
    cost_basis: float