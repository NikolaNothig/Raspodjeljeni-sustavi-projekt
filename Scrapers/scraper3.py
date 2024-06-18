# scraper3.py
from celery_worker import app
from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup

app_scraper3 = FastAPI()

def scrape_page(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve page {url}")
        return []
    
    soup = BeautifulSoup(response.content, "html.parser")
    products = []
    product_titles = soup.find_all("span", class_="field field--name-title field--type-string field--label-hidden")
    actual_prices = soup.find_all("span", class_="product__pricing-discount")
    old_prices = soup.find_all("div", class_="product--teaser__content-price--old")
    
    for title, actual_price, old_price in zip(product_titles, actual_prices, old_prices):
        old_price_text = old_price.find("div", class_="product--teaser__content-price--old-strike")
        products.append({
            "name": title.get_text(strip=True),
            "new_price": actual_price.get_text(strip=True),
            "old_price": old_price_text.get_text(strip=True) if old_price_text else "unknown"
        })
    return products

@app.task(name='scraper3.scrape3')
def scrape3(start_page, end_page):
    base_url = "https://www.svijet-medija.hr/akcije?items_per_page=24&sort_bef_combine=created_DESC&sort_by=created&sort_order=DESC&page=%2C%2C{page}"
    all_products = []
    
    for page_number in range(start_page, end_page + 1):
        url = base_url.format(page=page_number)
        products = scrape_page(url)
        if not products:
            print(f"No products found on page {page_number}. Stopping scraper.")
            break
        all_products.extend(products)
    return all_products

# celery -A scraper3 worker --loglevel=info -P eventlet -Q scraper3_queue
