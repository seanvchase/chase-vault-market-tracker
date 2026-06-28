def get_recommendation(purchase_price, current_price):
    """
    Gives a simple buy, hold, or sell recommendation.
    """

    if purchase_price == 0:
        return "No recommendation available"

    percent_change = ((current_price - purchase_price) / purchase_price) * 100

    if percent_change >= 25:
        return "Sell"
    elif percent_change <= -15:
        return "Buy/Hold"
    else:
        return "Hold"
