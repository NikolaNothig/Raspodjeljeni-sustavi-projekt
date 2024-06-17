from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup

app = FastAPI()

def scrape_page(url):
    title = "Svijet Medija"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to retrieve page {url}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    
    products = []
    product_titles = soup.find_all("span", class_="field field--name-title field--type-string field--label-hidden")
    actual_prices = soup.find_all("span", class_="product__pricing-discount")
    old_prices = soup.find_all("div", class_="product--teaser__content-price--old")
    
    if not product_titles or not actual_prices:
        print(f"No products found on page {url}")
        return []
    
    for title, actual_price, old_price in zip(product_titles, actual_prices, old_prices):
        product_name = title.get_text(strip=True)
        new_price = actual_price.get_text(strip=True)
        old_price_element = old_price.find("div", class_="product--teaser__content-price--old-strike")
        old_price_text = old_price_element.get_text(strip=True) if old_price_element else "unknown"
        
        products.append({
            "name": product_name,
            "new_price": new_price,
            "old_price": old_price_text
        })
    
    return products

@app.get("/")
async def scrape_all_pages():
    base_url = "https://www.svijet-medija.hr/akcije?items_per_page=24&sort_bef_combine=created_DESC&sort_by=created&sort_order=DESC&page=%2C%2C{page}"
    page_number = 0
    all_products = []
    
    while True:
        url = base_url.format(page=page_number)
        products = scrape_page(url)
        
        if not products:
            print(f"No products found on page {page_number}. Stopping scraper.")
            break
        
        all_products.extend(products)
        page_number += 1
        print(f"Scraped page number: {page_number}")
    
    print(f"Total products scraped: {len(all_products)}")
    return {"data": all_products, "title": "Svijet Medija"}

# Pokretanje: uvicorn scraper3:app --reload --port 8003
