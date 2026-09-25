import requests
from bs4 import BeautifulSoup
import logging
import pandas as pd
import json


INPUT_FILE = "product_urls.csv"
OUTPUT_FILE = "laptop_details.csv"


# Logging
logging.basicConfig(
    filename="../scraper_logs/laptop_details.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# Browser-like headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/153.0.0.0 Safari/537.36"
}


def get_product_urls():

    df = pd.read_csv(INPUT_FILE)

    product_urls = df["url"].tolist()

    print("Total product URLs:", len(product_urls))

    return product_urls


def scrape_product(url):

    response = requests.get(url, headers=headers)

    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")

    # Product name
    product_name = ""

    name = soup.find("h1")

    if name:
        product_name = name.get_text(" ", strip=True)

    # Price

    price = ""

    price_element = soup.find(
        "h2",
        class_="ps-product__price"
    )

    if price_element:
        price = price_element.get_text(" ", strip=True)

    availability = ""

    description = soup.find(
        "div",
        class_="ps-product__desc"
    )

    if description:

        paragraphs = description.find_all("p")

        for p in paragraphs:

            text = p.get_text(" ", strip=True)

            if "Availability:" in text:

                availability = text
                break

    # Features
    features = []

    description = soup.find(
        "div",
        class_="ps-product__specification"
    )

    if description:

        feature_items = description.find_all("li")

        for item in feature_items:

            feature = item.get_text(
                " ",
                strip=True
            )

            if feature:
                features.append(feature)

    # Specifications
    specifications = {}

    description_tab = soup.find(
        "div",
        id="tab-description"
    )

    if description_tab:

        rows = description_tab.find_all("tr")

        for row in rows:

            cells = row.find_all("td")

            if len(cells) == 2:

                key = cells[0].get_text(
                    " ",
                    strip=True
                )

                value = cells[1].get_text(
                    " ",
                    strip=True
                )

                if key:
                    specifications[key] = value

    # Product data
    product_data = {

        "url": url,

        "product_name": product_name,

        "price": price,

        "availability": availability,

        "features": " | ".join(features),

        "specifications": json.dumps(
            specifications,
            ensure_ascii=False
        )
    }


    return product_data


def main():

    product_urls = get_product_urls()

    scraped_data = []


    for url in product_urls:

        print("Scraping:", url)

        try:

            product_data = scrape_product(url)

            scraped_data.append(product_data)

            logger.info(
                "Product scraped successfully: %s",
                url
            )

        except Exception as e:

            logger.error(
                "Failed to scrape %s: %s",
                url,
                e
            )

            print(
                "Failed:",
                url
            )


    # Converts scraped data into DataFrame

    df = pd.DataFrame(scraped_data)


    # Save to CSV

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )


    print()
    print("Scraping completed.")
    print("Products scraped:", len(scraped_data))
    print("Product details saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()