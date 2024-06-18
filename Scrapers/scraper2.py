from celery_worker import app
from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup

app_scraper2 = FastAPI()

def scrape_page(url):
    title = "Sancta Domenica"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    
    products = []
    product_titles = soup.find_all("strong", class_="product name product-item-name")
    actual_prices = soup.find_all("span", class_="price-wrapper", attrs={"data-price-type": "finalPrice"})
    old_prices = soup.find_all("span", class_="price-wrapper", attrs={"data-price-type": "oldPrice"})
    
    old_prices_dict = {price.get('id'): price for price in old_prices}
    
    if not product_titles or not actual_prices:
        print(f"Missing elements on page {url}")
        return products
    
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

@app.task(name='scraper2.scrape2')
def scrape2(start_page, end_page):
    all_products = []
    
    for page_number in range(start_page, end_page + 1):
        url = f"https://www.sancta-domenica.hr/racunala-i-periferija/prijenosna-racunala.html?gad_source=1&p={page_number}&product_list_order=bestsellers"
        products = scrape_page(url)
        
        if not products:
            print(f"No products found on page {page_number}. Stopping scraper.")
            break
        
        all_products.extend(products)
    
    return all_products
#celery -A scraper2 worker --loglevel=info -P eventlet -Q scraper2_queue