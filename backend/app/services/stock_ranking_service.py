def rank_stocks(results):

    if not results:
        return []


    for stock in results:

        predicted_return = stock.get(
            "predicted_return_percent",
            0
        )

        confidence = stock.get(
            "confidence",
            0
        )


        stock["score"] = (
            predicted_return
            * confidence
        )


    ranked_stocks = sorted(

        results,

        key=lambda stock:
        stock["score"],

        reverse=True

    )


    return ranked_stocks