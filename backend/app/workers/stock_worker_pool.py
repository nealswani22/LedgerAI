from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed
)

from app.services.stock_ai_services import (
    analyze_stock_with_ai
)


def analyze_stocks_with_worker_pool(
    stocks,
    max_workers=5
):

    results = []


    if not stocks:
        return results


    with ThreadPoolExecutor(
        max_workers=max_workers
    ) as executor:

        future_to_stock = {

            executor.submit(
                analyze_stock_with_ai,
                stock
            ): stock

            for stock in stocks
        }


        for future in as_completed(
            future_to_stock
        ):

            stock = future_to_stock[
                future
            ]


            try:

                result = future.result()


                if result:

                    results.append(
                        result
                    )


            except Exception as error:

                print(
                    f"Worker failed for "
                    f"{stock.get('symbol')}: {error}"
                )


    return results