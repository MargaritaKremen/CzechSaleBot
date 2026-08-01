import json
from pathlib import Path

from utils.normalize import normalize_text

PRODUCTS_FILE = Path("data/products.json")
SAMPLE_PRODUCTS_FILE = Path("data/sample_products.json")
MAX_RESULTS = 5


def load_products() -> list[dict]:
    data_file = PRODUCTS_FILE if PRODUCTS_FILE.exists() else SAMPLE_PRODUCTS_FILE

    with open(data_file, "r", encoding="utf-8") as file:
        return json.load(file)


def split_product_queries(text: str) -> list[str]:                  # This function breaks the text down into a list of products
    items = text.replace("\n", ",").split(",")

    return [item.strip() for item in items if item.strip()]


def get_available_stores() -> list[str]:
    products = load_products()

    stores = set()

    for product in products:
        stores.add(product["store"])

    return sorted(stores)


def find_store_by_name(store_query: str) -> str | None:         # Перевірка чи існує введена назва магазину серед доступних
    normalized_store_query = normalize_text(store_query)

    for store in get_available_stores():
        normalized_store = normalize_text(store)

        if normalized_store_query == normalized_store:
            return store

    return None


def sort_products_by_price(products: list[dict]) -> list[dict]:
    return sorted(
        products,
        key=lambda product: float(str(product["price"]).replace(",", "."))
    )


def search_products(query: str) -> list[dict]:
    products = load_products()
    normalized_query = normalize_text(query)

    results = []

    for product in products:
        normalized_name = normalize_text(product["name"])
        normalized_store = normalize_text(product["store"])

        if normalized_query in normalized_name or normalized_query in normalized_store:
            results.append(product)

    return sort_products_by_price(results)

def search_products_by_name_and_store(product_query: str, store_query: str) -> list[dict]:
    products = load_products()

    normalized_product_query = normalize_text(product_query)
    normalized_store_query = normalize_text(store_query)

    results = []

    for product in products:
        normalized_name = normalize_text(product["name"])
        normalized_store = normalize_text(product["store"])

        if (
            normalized_product_query in normalized_name
            and normalized_store_query in normalized_store
        ):
            results.append(product)

    return sort_products_by_price(results)


def format_product(product: dict) -> str:
    lines = [
        f"🛒 {product['name']}",
        f"🏪 {product['store']}",
        f"💰 {product['price']} Kč",
        f"📅 Дійсно до: {product['valid_to']}",
    ]

    product_url = product.get("url")

    if product_url:
        lines.append(f'🌐 <a href="{product_url}">Сайт</a>')

    return "\n".join(lines)

def format_products(products: list[dict], total_count: int) -> str:
    if not products:
        return "Нічого не знайдено 😔"

    cheapest_product = products[0]
    other_products = products[1:]

    lines = [
        "✅ Найнижча ціна серед знайденого:\n",
        format_product(cheapest_product),
    ]

    if other_products:
        lines.append("\nІнші знайдені товари:\n")

        for product in other_products:
            lines.append(format_product(product))

    if total_count > len(products):
        lines.append(
            f"\nПоказано {len(products)} найдешевших результатів "
            f"із {total_count} знайдених."
        )

    return "\n\n".join(lines)