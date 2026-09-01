def calculate_investment_budget(
    current_balance: float,
    investment_percentage: float = 30
) -> float:

    if current_balance <= 0:
        return 0.0

    if investment_percentage < 0:
        return 0.0

    if investment_percentage > 100:
        return 0.0

    return round(
        current_balance * (
            investment_percentage / 100
        ),
        2
    )