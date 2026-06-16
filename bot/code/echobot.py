from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.code.settings import BOTTOKEN
from services.products import search_products, format_products

TOKEN = BOTTOKEN

dp = Dispatcher()


@dp.message(Command("search"))
async def search_handler(message: Message) -> None:
    query = message.text.replace("/search", "", 1).strip()

    if not query:
        await message.answer("Напиши товар після команди. Наприклад:\n/search milka")
        return

    products = search_products(query)
    response = format_products(products)

    await message.answer(response)

async def start_bot() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)