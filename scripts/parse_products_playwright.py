from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin
from pathlib import Path


BASE_URL = "https://www.akcniletak.cz"
OFFERS_PATH = "/nejlepe-hodnocene-nabidky"
MAX_PAGES = 3
DELAY_BETWEEN_PAGES_SECONDS = 2


def build_offers_page_url(page_number: int) -> str:
    return (
        f"{BASE_URL}{OFFERS_PATH}"
        f"?sort=votes_last_seven_days&page={page_number}"
    )


def fetch_page_with_browser(page, url: str) -> str | None:
    try:
        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        page.wait_for_selector(
            "a.js-offer-link-item",
            timeout=60000,
        )

        return page.content()

    except PlaywrightTimeoutError:
        print("Page loading timed out.")
        return None

    except Exception as error:
        print(f"Browser fetch failed: {error}")
        return None

def print_pagination_links(html: str) -> None:
    soup = BeautifulSoup(html, "html.parser")

    links = []

    for link in soup.select("a[href]"):
        href = link.get("href", "")
        text = link.get_text(" ", strip=True)

        href_lower = href.lower()
        text_lower = text.lower()

        if (
            "page" in href_lower
            or "strana" in href_lower
            or "další" in text_lower
            or "next" in text_lower
            or "více" in text_lower
        ):
            links.append((text, href))

    print(f"\nPagination-like links found: {len(links)}")

    for text, href in links[:50]:
        print("-" * 80)
        print(f"Text: {text}")
        print(f"Href: {href}")


def extract_products(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")

    product_cards = soup.select("a.js-offer-link-item")
    products = []

    for card in product_cards:
        name_element = card.select_one(".product__name")
        price_element = card.select_one(".product__price-offer")
        store_image = card.select_one(".store-image img")
        date_element = card.select_one(".product-date")

        if not name_element or not price_element or not store_image:
            continue

        product_url = urljoin(
            "https://www.akcniletak.cz",
            card.get("href", "")
        )

        product = {
            "name": name_element.get_text(strip=True),
            "store": store_image.get("alt", "").strip(),
            "price": price_element.get_text(strip=True).replace(" Kč", "").replace(",", "."),
            "valid_to": date_element.get_text(strip=True) if date_element else "",
            "url": product_url,
        }

        products.append(product)

    return products


def save_products_to_json(products: list[dict], file_path: str) -> None:
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(products, file, ensure_ascii=False, indent=2)


def get_total_pages(html: str) -> int:
    soup = BeautifulSoup(html, "html.parser")

    page_links = soup.select(".paginator__list a.btn--paginator-page")

    page_numbers = []

    for link in page_links:
        href = link.get("href", "")

        if "page=" not in href:
            continue

        try:
            page_number = int(href.split("page=")[-1].split("&")[0])
            page_numbers.append(page_number)
        except ValueError:
            continue

    return max(page_numbers) if page_numbers else 1


def main() -> None:
    all_products = []
    parsing_failed = False

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page(
            locale="cs-CZ",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )

        # Перша сторінка
        first_url = build_offers_page_url(1)
        print(f"\nParsing page 1: {first_url}")

        first_html = fetch_page_with_browser(page, first_url)

        if first_html is None:
            print("Could not load first page.")
            browser.close()
            return

        # Визначаємо реальну кількість сторінок
        total_pages = get_total_pages(first_html)
        print(f"Total pages found: {total_pages}")

        # Поки що для тесту беремо максимум 3 сторінки
        pages_to_parse = min(total_pages, 30)
        print(f"Pages to parse: {pages_to_parse}")

        # Товари з першої сторінки
        first_products = extract_products(first_html)

        print(
            f"Extracted products from page 1: "
            f"{len(first_products)}"
        )

        if not first_products:
            print("No products extracted from page 1.")
            parsing_failed = True
        else:
            all_products.extend(first_products)

        # Решта сторінок
        for page_number in range(2, pages_to_parse + 1):
            url = build_offers_page_url(page_number)
            print(f"\nParsing page {page_number}: {url}")

            html = fetch_page_with_browser(page, url)

            if html is None:
                print(f"No HTML received for page {page_number}.")
                parsing_failed = True
                continue

            products = extract_products(html)

            print(
                f"Extracted products from page {page_number}: "
                f"{len(products)}"
            )

            if not products:
                print(f"No products extracted from page {page_number}.")
                parsing_failed = True
                continue

            all_products.extend(products)

            if page_number < pages_to_parse:
                time.sleep(DELAY_BETWEEN_PAGES_SECONDS)

        browser.close()

    print(f"\nTotal extracted products: {len(all_products)}")

    if all_products and not parsing_failed:
        save_products_to_json(
            all_products,
            "data/products.json",
        )
        print("Saved products to data/products.json")
    else:
        print(
            "Parsing incomplete. "
            "Existing products.json was not changed."
        )


if __name__ == "__main__":
    main()