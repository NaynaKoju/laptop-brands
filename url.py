import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging
import pandas as pd


# Configuring logging
logging.basicConfig(
    filename="../scraper_logs/laptop_urls.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/153.0.0.0 Safari/537.36"
}


def get_brand_urls():
    url = "https://hexxone.com/laptops-by-brand"

    response = requests.get(url, headers=headers)

    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")

    links = soup.find_all("a")

    brand_urls = []

    for link in links:
        href = link.get("href")

        if href and "/laptops-by-brand/" in href:
            brand_urls.append(href)

    logger.info("Brand URLs collected: %s", len(brand_urls))
    print(len(brand_urls))

    return brand_urls


def get_product_urls(brand_url):

    # Get the first page
    page_url = brand_url + "?limit=30"

    response = requests.get(page_url, headers=headers)

    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")


    # Find pagination
    pagination = soup.find("ul", class_="pagination")

    total_pages = 1

    if pagination:

        page_links = pagination.find_all("a")

        for link in page_links:

            href = link.get("href")

            if href and "page=" in href:

                page_number = href.split("page=")[1]

                if page_number.isdigit():

                    page_number = int(page_number)

                    if page_number > total_pages:
                        total_pages = page_number


    print("Total pages:", total_pages)


    # Store all product URLs
    product_urls = []


    # Visit every page
    for page in range(1, total_pages + 1):

        if page == 1:
            page_url = brand_url + "?limit=30"

        else:
            page_url = brand_url + "?limit=30&page=" + str(page)


        print("Scraping:", page_url)


        response = requests.get(page_url, headers=headers)

        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")


        # Find product containers
        containers = soup.find_all(
            "div",
            class_="ps-container"
        )


        # Find products inside the containers
        for container in containers:

            products = container.find_all(
                "div",
                class_="ps-product"
            )


            for product in products:

                a_tag = product.find("a")


                if a_tag:

                    href = a_tag.get("href")


                    if href:

                        full_url = urljoin(page_url, href)

                        product_urls.append(full_url)


    logger.info(
        "Product URLs collected from %s: %s",
        brand_url,
        len(product_urls)
    )

    return product_urls


def main():

    # Get all brand URLs
    brand_urls = get_brand_urls()

    all_product_urls = []


    # Visit each brand page
    for brand_url in brand_urls:

        product_urls = get_product_urls(brand_url)

        all_product_urls.extend(product_urls)


    print("Total product URLs:", len(all_product_urls))


    # Create DataFrame
    df = pd.DataFrame({
        "url": all_product_urls
    })


    # Save URLs to CSV
    df.to_csv("product_urls.csv", index=False)

    print("Product URLs saved to product_urls.csv")


if __name__ == "__main__":
    main()