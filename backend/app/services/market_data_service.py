import os

import pandas as pd
import yfinance as yf


def get_stock_symbols():

    current_directory = os.path.dirname(
        os.path.abspath(__file__)
    )

    csv_path = os.path.join(
        current_directory,
        "..",
        "database",
        "EQUITY_L.csv"
    )

    stocks = pd.read_csv(
        csv_path
    )

    symbols = []

    for symbol in stocks["SYMBOL"]:

        if pd.isna(symbol):
            continue

        symbol = str(
            symbol
        ).strip()

        if not symbol:
            continue

        symbols.append(
            f"{symbol}.NS"
        )

    return symbols


def get_current_price(symbol: str):

    try:

        stock = yf.Ticker(
            symbol
        )

        history = stock.history(
            period="5d",
            interval="1d"
        )

        if history.empty:
            return None

        return round(
            float(
                history["Close"].iloc[-1]
            ),
            2
        )

    except Exception:

        return None


def get_stock_data(symbol: str):

    try:

        stock = yf.Ticker(
            symbol
        )

        history = stock.history(
            period="6mo",
            interval="1d"
        )

        if history.empty:
            return None

        current_price = float(
            history["Close"].iloc[-1]
        )

        return {

            "symbol":
            symbol,

            "current_price":
            round(
                current_price,
                2
            ),

            "history":
            history

        }

    except Exception:

        return None