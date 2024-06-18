from celery_worker import app
from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup

app_scraper1 = FastAPI()

def scrape_page(url):
    title = "Links"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    products = []
    product_titles = soup.find_all("h2", class_="product-title")
    actual_prices = soup.find_all("span", class_="price actual-price")
    old_prices = soup.find_all("span", class_="price old-price")
    
    if not product_titles or not actual_prices or not old_prices:
        print(f"Missing elements on page {url}")
        return products
    
    min_length = min(len(product_titles), len(actual_prices), len(old_prices))
    
    for i in range(min_length):
        try:
            product_name = product_titles[i].get_text(strip=True)
            new_price = actual_prices[i].get_text(strip=True)
            old_price_text = old_prices[i].get_text(strip=True)
            
            products.append({
                "name": product_name,
                "new_price": new_price,
                "old_price": old_price_text
            })
        except IndexError:
            print(f"Index error at page {url}, index {i}")
    
    return products

@app.task(name='scraper1.scrape1')
def scrape1(url):
    return scrape_page(url)

@app_scraper1.get("/")
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

#celery -A scraper1 worker --loglevel=info -P eventlet -Q scraper1_queue