import asyncio
import subprocess
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


PRAGUE_TZ = ZoneInfo("Europe/Prague")


async def run_parser_daily():
    while True:
        now = datetime.now(PRAGUE_TZ)

        next_run = now.replace(
            hour=2,
            minute=0,
            second=0,
            microsecond=0,
        )

        if next_run <= now:
            next_run += timedelta(days=1)

        wait_seconds = (next_run - now).total_seconds()

        print(f"Next products update: {next_run}")

        await asyncio.sleep(wait_seconds)

        print("Starting daily products parser...")

        result = await asyncio.to_thread(
            subprocess.run,
            [sys.executable, "scripts/parse_products_playwright.py"],
            check=False,
        )

        if result.returncode == 0:
            print("Products parser finished successfully.")
        else:
            print(
                f"Products parser failed with exit code "
                f"{result.returncode}"
            )