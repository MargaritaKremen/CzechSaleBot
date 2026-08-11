import asyncio

from bot.code.echobot import start_bot
from services.scheduler import run_parser_daily


async def main():
    scheduler_task = asyncio.create_task(run_parser_daily())

    try:
        await start_bot()
    finally:
        scheduler_task.cancel()


if __name__ == "__main__":
    asyncio.run(main())