from decimal import Decimal


PRODUCTS = [
    {
        "name": "Milka Čokoláda",
        "price": Decimal("27.90"),
        "store": "BILLA",
        "valid_to": "2026-06-02",
    },
    {
        "name": "Milka Čokoláda",
        "price": Decimal("31.90"),
        "store": "Tesco",
        "valid_to": "2026-06-04",
    },
    {
        "name": "Máslo",
        "price": Decimal("39.90"),
        "store": "Kaufland",
        "valid_to": "2026-06-02",
    },
]


def normalize_text(text: str) -> str:
    return text.lower().strip()


def search_products(query: str) -> list[dict]:
    query = normalize_text(query)

    result = []

    for product in PRODUCTS:
        product_name = normalize_text(product["name"])

        if query in product_name:
            result.append(product)

    return sorted(result, key=lambda item: item["price"])