from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup

app = FastAPI()

def scrape_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    products = []
    product_titles = soup.find_all("h2", class_="product-title")
    actual_prices = soup.find_all("span", class_="price actual-price")
    old_prices = soup.find_all("span", class_="price old-price")
    
    for title, actual_price, old_price in zip(product_titles, actual_prices, old_prices):
        product_name = title.get_text(strip=True)
        new_price = actual_price.get_text(strip=True)
        old_price_text = old_price.get_text(strip=True)
        
        products.append({
            "name": product_name,
            "new_price": new_price,
            "old_price": old_price_text
        })
    
    return products

@app.get("/")
async def scrape_all_pages():
    base_url = "https://www.links.hr/hr/discounted-products/informatika-01"
    page_number = 1
    all_products = []
    
    while True:
        url = f"{base_url}?pagenumber={page_number}"
        products = scrape_page(url)
        
        if not products:
            break
        
        all_products.extend(products)
        page_number += 1
    
    return {"data": all_products}

# Pokretanje: uvicorn scraper1:app --reload --port 8001
