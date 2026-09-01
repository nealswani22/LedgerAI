import pandas as pd


def calculate_stock_analytics(history):

    if history is None or history.empty:
        return None


    close_prices = history["Close"]


    current_price = float(
        close_prices.iloc[-1]
    )

    return_7d = None
    return_30d = None


    if len(close_prices) >= 8:

        return_7d = (
            (
                current_price
                - float(close_prices.iloc[-8])
            )
            / float(close_prices.iloc[-8])
        ) * 100


    if len(close_prices) >= 31:

        return_30d = (
            (
                current_price
                - float(close_prices.iloc[-31])
            )
            / float(close_prices.iloc[-31])
        ) * 100



    ma_20 = None
    ma_50 = None


    if len(close_prices) >= 20:

        ma_20 = float(
            close_prices.tail(20).mean()
        )


    if len(close_prices) >= 50:

        ma_50 = float(
            close_prices.tail(50).mean()
        )



    daily_returns = close_prices.pct_change().dropna()


    volatility = None


    if not daily_returns.empty:

        volatility = float(
            daily_returns.std()
            * (252 ** 0.5)
            * 100
        )


    rsi = None


    if len(close_prices) >= 15:

        delta = close_prices.diff()

        gains = delta.clip(
            lower=0
        )

        losses = -delta.clip(
            upper=0
        )

        average_gain = gains.tail(14).mean()

        average_loss = losses.tail(14).mean()


        if average_loss == 0:

            rsi = 100.0

        else:

            relative_strength = (
                average_gain
                / average_loss
            )

            rsi = (
                100
                - (
                    100
                    / (
                        1
                        + relative_strength
                    )
                )
            )



    return {

        "current_price":
        round(current_price, 2),

        "return_7d":
        round(return_7d, 2)
        if return_7d is not None
        else None,

        "return_30d":
        round(return_30d, 2)
        if return_30d is not None
        else None,

        "ma_20":
        round(ma_20, 2)
        if ma_20 is not None
        else None,

        "ma_50":
        round(ma_50, 2)
        if ma_50 is not None
        else None,

        "volatility":
        round(volatility, 2)
        if volatility is not None
        else None,

        "rsi":
        round(float(rsi), 2)
        if rsi is not None
        else None

    }