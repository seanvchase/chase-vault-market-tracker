def search_ebay_cards(card_name):
    """
    Placeholder function for eBay card search.
    Later, this will connect to the real eBay API.
    """
    sample_results = [
        {"title": f"{card_name} trading card", "price": 25.99, "condition": "Near Mint"},
        {"title": f"{card_name} foil card", "price": 39.99, "condition": "Lightly Played"},
        {"title": f"{card_name} graded PSA 10", "price": 149.99, "condition": "Graded"},
    ]

    return sample_results
