from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup

app = FastAPI()

def scrape_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    products = []
    product_titles = soup.find_all("strong", class_="product name product-item-name")
    actual_prices = soup.find_all("span", class_="price-wrapper", attrs={"data-price-type": "finalPrice"})
    old_prices = soup.find_all("span", class_="price-wrapper", attrs={"data-price-type": "oldPrice"})
    
    old_prices_dict = {price.get('id'): price for price in old_prices}
    
    for title, actual_price in zip(product_titles, actual_prices):
        product_name = title.get_text(strip=True)
        new_price = actual_price.get_text(strip=True)
        old_price_id = actual_price.get('id').replace('product-price', 'old-price')
        old_price_element = old_prices_dict.get(old_price_id)
        
        if old_price_element:
            old_price_text = old_price_element.get_text(strip=True)
            products.append({
                "name": product_name,
                "new_price": new_price,
                "old_price": old_price_text
            })
    
    return products

@app.get("/")
async def scrape_all_pages():
    base_url = "https://www.sancta-domenica.hr/racunala-i-periferija/prijenosna-racunala.html?gad_source=1&p={page}&product_list_order=bestsellers"
    page_number = 0
    all_products = []
    
    while True:
        url = base_url.format(page=page_number)
        products = scrape_page(url)
        
        if not products:
            break
        
        all_products.extend(products)
        page_number += 1
    
    return {"data": all_products}

# Pokretanje: uvicorn scraper2:app --reload --port 8002
