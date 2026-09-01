from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from app.database.base import Base


class Transaction(Base):

    __tablename__ = "transactions"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    transaction_date = Column(
        DateTime,
        nullable=False
    )


    description = Column(
        String,
        nullable=False
    )


    normalized_description = Column(
        String,
        nullable=True,
        index=True
    )


    amount = Column(
        Float,
        nullable=False
    )


    transaction_type = Column(
        String,
        nullable=False
    )


    category = Column(
        String,
        nullable=True
    )


    merchant_name = Column(
        String,
        nullable=True
    )


    category_confidence = Column(
        Float,
        nullable=True
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )