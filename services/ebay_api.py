from urllib.parse import quote_plus


def search_ebay_cards(card_name):
    """
    Placeholder function for eBay card search.

    Later, this will connect to the real eBay API and return
    live listings with title, price, condition, image, and link.
    """

    search_term = quote_plus(card_name)

    sample_results = [
        {
            "title": f"{card_name} trading card",
            "price": 25.99,
            "condition": "Near Mint",
            "image_url": "https://placehold.co/240x336?text=Card+Image",
            "item_url": f"https://www.ebay.com/sch/i.html?_nkw={search_term}"
        },
        {
            "title": f"{card_name} foil card",
            "price": 39.99,
            "condition": "Lightly Played",
            "image_url": "https://placehold.co/240x336?text=Foil+Card",
            "item_url": f"https://www.ebay.com/sch/i.html?_nkw={search_term}+foil"
        },
        {
            "title": f"{card_name} graded PSA 10",
            "price": 149.99,
            "condition": "Graded",
            "image_url": "https://placehold.co/240x336?text=PSA+10",
            "item_url": f"https://www.ebay.com/sch/i.html?_nkw={search_term}+PSA+10"
        },
    ]

    return sample_results
