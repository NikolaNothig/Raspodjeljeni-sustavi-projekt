from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.templating import Jinja2Templates
from scraper1 import scrape1
from scraper2 import scrape2
from scraper3 import scrape3
from celery.result import AsyncResult
import logging
import pymongo
import asyncio
import httpx

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mongoclient = pymongo.MongoClient(
    "mongodb+srv://nnothig:12345@data.mfmvqb8.mongodb.net/?retryWrites=true&w=majority&appName=Data"
)
db = mongoclient["Baza_artikala"]
Artikli = db["Artikli"]

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

def create_scraper_tasks(scraper, start_page, end_page, num_workers=10):
    task_ids = []
    pages_per_worker = (end_page - start_page + 1) // num_workers
    for i in range(num_workers):
        sp = start_page + i * pages_per_worker
        ep = sp + pages_per_worker - 1
        if ep > end_page:
            ep = end_page
        task = scraper.delay(sp, ep)
        logger.info(f"Task created for pages: {sp} to {ep} with ID: {task.id}")
        task_ids.append(task.id)
    return task_ids

async def wait_for_tasks(task_ids):
    all_products = []
    for task_id in task_ids:
        task_result = AsyncResult(task_id)
        while task_result.state not in ['SUCCESS', 'FAILURE']:
            await asyncio.sleep(1)  # Check every second
            task_result = AsyncResult(task_id)
        if task_result.state == 'SUCCESS':
            logger.info(f"Task {task_id} completed successfully.")
            all_products.extend(task_result.result)
        else:
            logger.error(f"Task {task_id} failed with error: {task_result.result}")
    return all_products

@app.post("/scrape_all")
async def scrape_all(background_tasks: BackgroundTasks):
    async with httpx.AsyncClient() as client:
        response = await client.delete('http://localhost:8004/clear_data')
        logger.info(f"Cleared data: {response.json()['message']}")

    scraper1_tasks = create_scraper_tasks(scrape1, 1, 50)
    scraper2_tasks = create_scraper_tasks(scrape2, 1, 50)
    scraper3_tasks = create_scraper_tasks(scrape3, 1, 100)
    all_tasks = scraper1_tasks + scraper2_tasks + scraper3_tasks
    background_tasks.add_task(save_results_to_mongo, all_tasks)
    return {"message": "Scrapers started"}

async def save_results_to_mongo(task_ids):
    all_results = await wait_for_tasks(task_ids)
    if all_results:
        result = Artikli.insert_many(all_results)
        logger.info(f"Data saved to MongoDB. Inserted IDs: {result.inserted_ids}")
    else:
        logger.warning("No results to save to MongoDB.")

# uvicorn main:app --reload --port 8000
