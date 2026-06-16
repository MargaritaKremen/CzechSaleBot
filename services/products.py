import json
from pathlib import Path

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from utils.normalize import normalize_text


router = Router()

DATA_FILE = Path("data/sample_products.json")


def load_products() -> list[dict]:
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def search_products(query: str) -> list[dict]:
    products = load_products()
    normalized_query = normalize_text(query)

    results = []

    for product in products:
        normalized_name = normalize_text(product["name"])

        if normalized_query in normalized_name:
            results.append(product)

    return results


def format_products(products: list[dict]) -> str:
    if not products:
        return "Нічого не знайдено 😔"

    lines = ["Знайдено товари:\n"]

    for product in products:
        lines.append(
            f"🛒 {product['name']}\n"
            f"🏪 {product['store']}\n"
            f"💰 {product['price']} Kč\n"
            f"📅 Дійсно до: {product['valid_to']}"
        )

    return "\n".join(lines)


@router.message(Command("search"))
async def search_command(message: Message):
    query = message.text.replace("/search", "").strip()

    if not query:
        await message.answer("Напиши товар після команди, наприклад: /search cokolada")
        return

    products = search_products(query)
    response = format_products(products)

    await message.answer(response)