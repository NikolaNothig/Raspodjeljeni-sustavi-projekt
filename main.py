from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Ziv sam"}

@app.get("/scrape")
async def scrape_endpoint():
    data = scrape_function()
    return {"scraped_data": data}

#uvicorn main:app --reload --port 8000