from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def scrape():
    # Logika za scraping
    return {"data": "Scraped data from scraper 2"}

#uvicorn scraper:app --reload --port 8002