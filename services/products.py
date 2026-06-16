import json
from pathlib import Path

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from utils.normalize import normalize_text


router = Router()

DATA_FILE = Path("data/sample_products.json")
MAX_RESULTS = 5


def load_products() -> list[dict]:
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def sort_products_by_price(products: list[dict]) -> list[dict]:
    return sorted(products, key=lambda product: product["price"])


def search_products(query: str) -> list[dict]:
    products = load_products()
    normalized_query = normalize_text(query)

    results = []

    for product in products:
        normalized_name = normalize_text(product["name"])
        normalized_store = normalize_text(product["store"])

        if normalized_query in normalized_name or normalized_query in normalized_store:
            results.append(product)

    sorted_results = sort_products_by_price(results)
    return sorted_results[:MAX_RESULTS]


def format_products(products: list[dict]) -> str:
    if not products:
        return "Нічого не знайдено 😔"

    cheapest_product = products[0]
    other_products = products[1:]

    lines = [
        "✅ Найдешевший варіант:\n",
        f"🛒 {cheapest_product['name']}\n"
        f"🏪 {cheapest_product['store']}\n"
        f"💰 {cheapest_product['price']} Kč\n"
        f"📅 Дійсно до: {cheapest_product['valid_to']}"
    ]

    if other_products:
        lines.append("\nІнші знайдені товари:\n")

        for product in other_products:
            lines.append(
                f"🛒 {product['name']}\n"
                f"🏪 {product['store']}\n"
                f"💰 {product['price']} Kč\n"
                f"📅 Дійсно до: {product['valid_to']}"
            )

    return "\n\n".join(lines)


@router.message(Command("search"))
async def search_command(message: Message):
    query = message.text.replace("/search", "").strip()

    if not query:
        await message.answer("Напиши товар після команди, наприклад: /search cokolada")
        return

    products = search_products(query)
    response = format_products(products)

    await message.answer(response)