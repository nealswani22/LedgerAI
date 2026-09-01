from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TransactionCreate(BaseModel):
    transaction_date: datetime
    description: str
    amount: float
    transaction_type: str


class TransactionResponse(BaseModel):
    id: int
    transaction_date: datetime
    description: str
    amount: float
    transaction_type: str

    category: Optional[str] = None
    merchant_name: Optional[str] = None
    category_confidence: Optional[float] = None

    class Config:
        from_attributes = True