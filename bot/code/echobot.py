from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.code.settings import BOTTOKEN
from services.products import search_products

TOKEN = BOTTOKEN

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Привіт, {html.bold(message.from_user.full_name)}!\n\n"
        "Я бот для пошуку акційних цін у чеських супермаркетах.\n\n"
        "Спробуй команду:\n"
        "/search milka"
    )


@dp.message(Command("help"))
async def help_handler(message: Message) -> None:
    await message.answer(
        "Команди:\n"
        "/search milka — знайти товар\n"
        "/search maslo — знайти масло"
    )


@dp.message(Command("search"))
async def search_handler(message: Message) -> None:
    query = message.text.replace("/search", "", 1).strip()

    if not query:
        await message.answer("Напиши товар після команди. Наприклад:\n/search milka")
        return

    products = search_products(query)

    if not products:
        await message.answer("Нічого не знайшла.")
        return

    lines = ["Знайдено:"]

    for product in products:
        lines.append(
            f"\n{product['name']}\n"
            f"{product['store']} — {product['price']} Kč\n"
            f"Дійсно до: {product['valid_to']}"
        )

    await message.answer("\n".join(lines))


@dp.message()
async def unknown_message_handler(message: Message) -> None:
    await message.answer(
        "Я поки розумію тільки команди.\n"
        "Спробуй:\n"
        "/search milka"
    )


async def start_bot() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)