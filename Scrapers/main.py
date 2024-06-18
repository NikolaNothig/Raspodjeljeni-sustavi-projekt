from fastapi import FastAPI, HTTPException, BackgroundTasks
from scraper1 import scrape1
from scraper2 import scrape2
from scraper3 import scrape3
from celery.result import AsyncResult
import logging
import pymongo
import asyncio

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB client setup
mongoclient = pymongo.MongoClient(
    "mongodb+srv://nnothig:12345@data.mfmvqb8.mongodb.net/?retryWrites=true&w=majority&appName=Data"
)
db = mongoclient["Baza_artikala"]  
Artikli = db["Artikli"]

@app.get("/")
async def root():
    return {"message": "Service is running"}

def create_scraper_tasks(scraper, start_page, end_page, num_workers=30):
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

@app.post("/scrape/{scraper_name}")
async def start_scraping(scraper_name: str, start_page: int, end_page: int, background_tasks: BackgroundTasks):
    if scraper_name == 'scraper1':
        tasks = create_scraper_tasks(scrape1, start_page, end_page)
    elif scraper_name == 'scraper2':
        tasks = create_scraper_tasks(scrape2, start_page, end_page)
    elif scraper_name == 'scraper3':
        tasks = create_scraper_tasks(scrape3, start_page, end_page)
    else:
        raise HTTPException(status_code=404, detail="Scraper not found")
    
    # Add task to wait for all scrapers to finish and save results
    background_tasks.add_task(save_results_to_mongo, tasks)
    
    return {"task_ids": tasks}

async def save_results_to_mongo(task_ids):
    all_results = await wait_for_tasks(task_ids)
    if all_results:
        # Save results to MongoDB
        result = Artikli.insert_many(all_results)
        logger.info(f"Data saved to MongoDB. Inserted IDs: {result.inserted_ids}")
    else:
        logger.warning("No results to save to MongoDB.")

# Running the server with: uvicorn main:app --reload --port 8000
