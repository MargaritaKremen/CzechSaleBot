from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from bot.code.settings import BOTTOKEN
from services.products import (
    search_products,
    search_products_by_name_and_store,
    get_available_stores,
    find_store_by_name,
    format_products,
    MAX_RESULTS,
    split_product_queries,
)

TOKEN = BOTTOKEN

dp = Dispatcher()

user_search_modes = {}
user_selected_stores = {}

SEARCH_PRODUCT_BUTTON = "🔍 Пошук за товаром"
SEARCH_STORE_BUTTON = "🏪 Пошук в магазині"
HELP_BUTTON = "ℹ️ Допомога"
STORES_BUTTON = "📃 Доступні магазини"
CANCEL_BUTTON = "↩️ Скасувати"

MENU_BUTTONS = {
    SEARCH_PRODUCT_BUTTON,
    SEARCH_STORE_BUTTON,
    HELP_BUTTON,
    STORES_BUTTON,
    CANCEL_BUTTON,
}

MODE_PRODUCT = "product"
MODE_WAITING_FOR_STORE = "waiting_for_store"
MODE_WAITING_FOR_PRODUCT_IN_STORE = "waiting_for_product_in_store"


main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=SEARCH_PRODUCT_BUTTON)],
        [KeyboardButton(text=SEARCH_STORE_BUTTON)],
        [KeyboardButton(text=HELP_BUTTON)],
        [KeyboardButton(text=STORES_BUTTON)],
        [KeyboardButton(text=CANCEL_BUTTON)],
    ],
    resize_keyboard=True
)


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    start_text = (
        "Привіт! 🛒\n\n"
        "Я CzechSaleBot — допомагаю шукати акційні товари "
        "в чеських супермаркетах.\n\n"
        "Обери режим пошуку:\n\n"
        "🔍 Пошук за товаром — знайти товар у всіх магазинах\n"
        "🏪 Пошук в магазині — спочатку обрати магазин, потім товар\n\n"
        "Якщо передумаєш — натисни ↩️ Скасувати."
    )

    await message.answer(start_text, reply_markup=main_keyboard)


@dp.message(Command("search"))
async def search_handler(message: Message) -> None:
    query = message.text.replace("/search", "", 1).strip()

    if not query:
        await message.answer("Напиши товар після команди. Наприклад:\n/search milka")
        return

    all_products = search_products(query)

    await send_search_results(
        message,
        all_products,
        not_found_message=f"Нічого не знайдено за запитом: {query} 😔",
    )


async def send_help(message: Message) -> None:
    help_text = (
        "🛒 CzechSaleBot допомагає шукати акційні товари в чеських супермаркетах.\n\n"
        "Як користуватися:\n\n"
        "🔍 Пошук за товаром\n"
        "Натисни кнопку і напиши назву товару.\n"
        "Наприклад:\n"
        "milka\n"
        "mleko\n"
        "cokolada\n\n"
        "🏪 Пошук в магазині\n"
        "Натисни кнопку, напиши магазин, а потім товар.\n"
        "Наприклад:\n"
        "lidl → milka\n"
        "tesco → mleko\n\n"
        "📃 Доступні магазини\n"
        "Показує список магазинів, які є в базі.\n\n"
        "↩️ Скасувати\n"
        "Скидає поточну дію і повертає до меню.\n\n"
        "Команди:\n"
        "/stores — показати доступні магазини\n"
        "/help — показати довідку\n\n"
        "Бот показує найдешевші результати першими."
    )

    await message.answer(help_text, reply_markup=main_keyboard)

@dp.message(Command("help"))
async def help_handler(message: Message) -> None:
    await send_help(message)

@dp.message(lambda message: message.text == HELP_BUTTON)
async def help_button_handler(message: Message) -> None:
    await send_help(message)


async def send_available_stores(message: Message) -> None:
    stores = get_available_stores()

    if not stores:
        await message.answer(
            "Список магазинів поки порожній 😔",
            reply_markup=main_keyboard,
        )
        return

    stores_text = "\n".join(f"🏪 {store}" for store in stores)

    await message.answer(
        "Доступні магазини:\n\n"
        f"{stores_text}",
        reply_markup=main_keyboard,
    )


@dp.message(Command("stores"))
async def stores_handler(message: Message) -> None:
    await send_available_stores(message)


@dp.message(lambda message: message.text == STORES_BUTTON)     # Доступні магазини
async def stores_button_handler(message: Message) -> None:
    await send_available_stores(message)


@dp.message(lambda message: message.text == CANCEL_BUTTON)
async def cancel_handler(message: Message) -> None:
    user_id = message.from_user.id

    user_search_modes.pop(user_id, None)
    user_selected_stores.pop(user_id, None)

    await message.answer(
        "Дію скасовано. Обери новий режим пошуку.",
        reply_markup=main_keyboard,
    )

@dp.message(lambda message: message.text == SEARCH_PRODUCT_BUTTON)       # Пошук за товаром
async def search_by_product_button_handler(message: Message) -> None:
    user_search_modes[message.from_user.id] = MODE_PRODUCT

    await message.answer(
        "Напиши назву товару без /search.\n\n"
        "Наприклад:\n"
        "milka\n"
        "mleko\n"
        "cokolada"
    )

@dp.message(lambda message: message.text == SEARCH_STORE_BUTTON)         # 🏪 Пошук в магазині
async def search_by_store_button_handler(message: Message) -> None:
    user_search_modes[message.from_user.id] = MODE_WAITING_FOR_STORE
    user_selected_stores.pop(message.from_user.id, None)

    await message.answer(
        "Напиши назву магазину.\n\n"
        "Наприклад:\n"
        "lidl\n"
        "tesco\n"
        "kaufland"
    )


async def send_search_results(
    message: Message,
    products: list[dict],
    not_found_message: str = "Нічого не знайдено 😔",
) -> None:
    if not products:
        await message.answer(not_found_message, reply_markup=main_keyboard)
        return

    visible_products = products[:MAX_RESULTS]
    response = format_products(visible_products, total_count=len(products))

    await message.answer(response, reply_markup=main_keyboard)


async def send_multiple_product_results(message: Message, queries: list[str]) -> None:      # This helper function returns the result in blocks
    responses = []

    for query in queries:
        products = search_products(query)
        visible_products = products[:MAX_RESULTS]

        if not products:
            responses.append(f"🔎 {query}\nНічого не знайдено 😔")
            continue

        response = format_products(visible_products, total_count=len(products))
        responses.append(f"🔎 {query}\n\n{response}")

    await message.answer("\n\n--------------------\n\n".join(responses), reply_markup=main_keyboard)


@dp.message()
async def text_search_handler(message: Message) -> None:
    user_id = message.from_user.id
    query = message.text.strip()

    search_mode = user_search_modes.get(user_id)

    if search_mode == MODE_PRODUCT:
        queries = split_product_queries(query)
        queries = [item for item in queries if item not in MENU_BUTTONS]     # запобігаю попаданню назви кнопки в продукти, які шукають

        user_search_modes.pop(user_id, None)
        user_selected_stores.pop(user_id, None)

        if not queries:
            await message.answer(
                "Напиши назву товару.\n\n"
                "Наприклад:\n"
                "milka\n"
                "mleko\n"
                "cokolada",
                reply_markup=main_keyboard,
            )
            return

        if len(queries) == 1:
            all_products = search_products(queries[0])

            await send_search_results(
                message,
                all_products,
                not_found_message=f"Нічого не знайдено за запитом: {queries[0]} 😔",
            )
            return

        await send_multiple_product_results(message, queries)
        return

    if search_mode == MODE_WAITING_FOR_STORE:
        store = find_store_by_name(query)

        if store is None:
            stores = get_available_stores()
            stores_text = "\n".join(f"🏪 {store}" for store in stores)

            await message.answer(
                "Такого магазину поки немає в базі 😔\n\n"
                "Доступні магазини:\n\n"
                f"{stores_text}\n\n"
                "Напиши назву магазину ще раз або натисни ↩️ Скасувати.",
                reply_markup=main_keyboard,
            )
            return

        user_selected_stores[user_id] = store
        user_search_modes[user_id] = MODE_WAITING_FOR_PRODUCT_IN_STORE

        await message.answer(
            f"Добре, шукаємо в магазині: {store}\n\n"
            "Тепер напиши, який товар шукати.\n\n"
            "Наприклад:\n"
            "milka\n"
            "mleko\n"
            "cokolada"
        )
        return

    if search_mode == MODE_WAITING_FOR_PRODUCT_IN_STORE:
        store_query = user_selected_stores.get(user_id)

        all_products = search_products_by_name_and_store(
            product_query=query,
            store_query=store_query,
        )

        user_search_modes.pop(user_id, None)
        user_selected_stores.pop(user_id, None)

        await send_search_results(
            message,
            all_products,
            not_found_message=f"У магазині {store_query} не знайдено товар: {query} 😔",
        )
        return

    await message.answer(
        "Спочатку обери режим пошуку кнопкою нижче:\n\n"
        "🔍 Пошук за товаром\n"
        "🏪 Пошук в магазині",
        reply_markup=main_keyboard,
    )


async def start_bot() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)