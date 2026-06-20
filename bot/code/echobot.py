from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from bot.code.settings import BOTTOKEN
from services.products import search_products, format_products, MAX_RESULTS

TOKEN = BOTTOKEN

dp = Dispatcher()

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 Пошук за товаром")],
        [KeyboardButton(text="🏪 Пошук в магазині")],
        [KeyboardButton(text="ℹ️ Допомога")],
    ],
    resize_keyboard=True
)


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    start_text = (
        "Привіт! 🛒\n\n"
        "Я CzechSaleBot — допомагаю шукати акційні товари "
        "в чеських супермаркетах.\n\n"
        "Обери, як ти хочеш шукати:\n\n"
        "🔍 Пошук за товаром — знайти товар у всіх магазинах\n"
        "🏪 Пошук в магазині — спочатку обрати магазин, потім товар\n\n"
        "Скористайся кнопками нижче."
    )

    await message.answer(start_text, reply_markup=main_keyboard)


@dp.message(Command("search"))
async def search_handler(message: Message) -> None:
    query = message.text.replace("/search", "", 1).strip()

    if not query:
        await message.answer("Напиши товар після команди. Наприклад:\n/search milka")
        return

    all_products = search_products(query)
    visible_products = all_products[:MAX_RESULTS]

    response = format_products(visible_products, total_count=len(all_products))

    await message.answer(response)

@dp.message(Command("help"))
async def help_handler(message: Message) -> None:
    help_text = (
        "🛒 CzechSaleBot допомагає шукати акційні товари в супермаркетах.\n\n"
        "Як користуватися:\n\n"
        "🔍 Пошук за товаром\n"
        "Натисни кнопку і напиши назву товару, наприклад:\n"
        "milka\n"
        "mleko\n"
        "cokolada\n\n"
        "🏪 Пошук в магазині\n"
        "Натисни кнопку, напиши магазин, а потім товар.\n"
        "Наприклад:\n"
        "lidl → milka\n"
        "tesco → mleko\n\n"
        "Поки що також працює команда:\n"
        "/search milka\n\n"
        "Бот показує найдешевші результати першими."
    )

    await message.answer(help_text)

@dp.message(lambda message: message.text == "ℹ️ Допомога")
async def help_button_handler(message: Message) -> None:
    await help_handler(message)


@dp.message(lambda message: message.text == "🔍 Пошук за товаром")
async def search_by_product_button_handler(message: Message) -> None:
    await message.answer(
        "Напиши назву товару без /search.\n\n"
        "Наприклад:\n"
        "milka\n"
        "mleko\n"
        "cokolada"
    )


@dp.message(lambda message: message.text == "🏪 Пошук в магазині")
async def search_by_store_button_handler(message: Message) -> None:
    await message.answer(
        "Напиши назву магазину.\n\n"
        "Наприклад:\n"
        "lidl\n"
        "tesco\n"
        "kaufland"
    )


async def start_bot() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)