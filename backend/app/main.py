from fastapi import FastAPI
from sqlalchemy import text
from app.routers.statements import router as statements_router
from app.database.connection import engine
from app.database.base import Base
from app.models.transaction import Transaction
from app.routers.transactions import router as transactions_router


app = FastAPI(
    title="FinanceBuddy API",
    version="0.1.0"
)


Base.metadata.create_all(bind=engine)

app.include_router(transactions_router)
app.include_router(statements_router)

@app.get("/")
def root():
    return {
        "message": "FinanceBuddy API is running"
    }


@app.get("/health/database")
def database_health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "database": "connected"
        }

    except Exception as error:
        return {
            "database": "error",
            "detail": str(error)
        }