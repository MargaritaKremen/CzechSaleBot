import json
from decimal import Decimal
from pathlib import Path
import unicodedata


BASE_DIR = Path(__file__).resolve().parent.parent
PRODUCTS_FILE = BASE_DIR / "data" / "sample_products.json"


def load_products() -> list[dict]:
    with open(PRODUCTS_FILE, "r", encoding="utf-8") as file:
        raw_products = json.load(file)

    products = []

    for product in raw_products:
        products.append({
            "name": product["name"],
            "price": Decimal(product["price"]),
            "store": product["store"],
            "valid_to": product["valid_to"],
        })

    return products


def normalize_text(text: str) -> str:
    text = text.lower().strip()

    text = unicodedata.normalize("NFD", text)
    text = "".join(
        char for char in text
        if unicodedata.category(char) != "Mn"
    )

    return text


def search_products(query: str) -> list[dict]:
    query = normalize_text(query)
    products = load_products()

    result = []

    for product in products:
        product_name = normalize_text(product["name"])

        if query in product_name:
            result.append(product)

    return sorted(result, key=lambda item: item["price"])