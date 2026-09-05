from typing import Optional
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str

class Holding(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    asset: str
    type: str
    quantity: float
    cost_basis: float
    user_id: int = Field(foreign_key="user.id")