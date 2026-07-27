from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from pathlib import Path
from bs4 import BeautifulSoup
import json
from pathlib import Path


URL = "https://www.akcniletak.cz/nejlepe-hodnocene-nabidky"


def fetch_page_with_browser(url: str) -> str | None:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page(
                locale="cs-CZ",
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
            )

            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(10000)

            html = page.content()

            print(f"Page title: {page.title()}")
            print(f"Final URL: {page.url}")
            print(f"HTML length: {len(html)}")
            print("First 500 characters:")
            print(html[:500])

            browser.close()

            return html

    except PlaywrightTimeoutError:
        print("Page loading timed out.")
        return None

    except Exception as error:
        print(f"Browser fetch failed: {error}")
        return None


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

        product = {
            "name": name_element.get_text(strip=True),
            "store": store_image.get("alt", "").strip(),
            "price": price_element.get_text(strip=True).replace(" Kč", "").replace(",", "."),
            "valid_to": date_element.get_text(strip=True) if date_element else "",
        }

        products.append(product)

    return products


def save_products_to_json(products: list[dict], file_path: str) -> None:
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(products, file, ensure_ascii=False, indent=2)


def main() -> None:
    html = fetch_page_with_browser(URL)

    if html is None:
        print("No HTML received.")
        return

    debug_file = Path("data/debug_page.html")
    debug_file.write_text(html, encoding="utf-8")
    print(f"Saved HTML to {debug_file}")

    products = extract_products(html)

    print(f"Extracted products: {len(products)}")

    for product in products[:10]:
        print(product)

    save_products_to_json(products, "data/parsed_products.json")
    print("Saved products to data/parsed_products.json")

    if "awsWaf" in html or "challenge" in html.lower():
        print("AWS WAF challenge is still present.")
    else:
        print("Looks like normal HTML.")


if __name__ == "__main__":
    main()