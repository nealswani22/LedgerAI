from concurrent.futures import ThreadPoolExecutor, as_completed

from app.services.market_data_service import (
    get_stock_symbols,
    get_current_price,
    get_stock_data
)

from app.services.stock_analytics import (
    calculate_stock_analytics
)

from app.workers.stock_worker_pool import (
    analyze_stocks_with_worker_pool
)

from app.services.stock_ranking_service import (
    rank_stocks
)


def check_stock_affordability(
    symbol,
    investment_budget
):

    current_price = get_current_price(
        symbol
    )

    if current_price is None:
        return None

    if current_price * 5 <= investment_budget:
        return symbol

    return None


def prepare_stock_for_ai(
    symbol
):

    stock_data = get_stock_data(
        symbol
    )

    if not stock_data:
        return None

    analytics = calculate_stock_analytics(
        stock_data["history"]
    )

    if not analytics:
        return None

    return {
        "symbol": symbol,
        **analytics
    }


def get_stock_recommendations(
    investment_budget
):

    symbols = get_stock_symbols()

    affordable_symbols = []


    with ThreadPoolExecutor(
        max_workers=10
    ) as executor:

        futures = {

            executor.submit(
                check_stock_affordability,
                symbol,
                investment_budget
            ): symbol

            for symbol in symbols
        }


        for future in as_completed(
            futures
        ):

            affordable_symbol = future.result()

            if affordable_symbol:

                affordable_symbols.append(
                    affordable_symbol
                )


    stocks_for_ai = []


    with ThreadPoolExecutor(
        max_workers=10
    ) as executor:

        futures = {

            executor.submit(
                prepare_stock_for_ai,
                symbol
            ): symbol

            for symbol in affordable_symbols
        }


        for future in as_completed(
            futures
        ):

            stock_for_ai = future.result()

            if stock_for_ai:

                stocks_for_ai.append(
                    stock_for_ai
                )


    ai_results = (
        analyze_stocks_with_worker_pool(

            stocks=stocks_for_ai,

            max_workers=5
        )
    )


    ranked_stocks = rank_stocks(
        ai_results
    )


    return ranked_stocks[:5]