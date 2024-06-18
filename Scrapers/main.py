from fastapi import FastAPI, HTTPException
from scraper1 import scrape1
from celery.result import AsyncResult
import json
import logging

app = FastAPI()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
async def root():
    return {"message": "Service is running"}

def create_scraper_tasks(start_page, end_page):
    task_ids = []
    for page_number in range(start_page, end_page + 1):
        url = f"https://www.links.hr/hr/discounted-products/informatika-01?pagenumber={page_number}"
        task = scrape1.delay(url)
        logger.info(f"Task created for URL: {url} with ID: {task.id}")
        task_ids.append(task.id)
    return task_ids

@app.post("/scrape/")
async def start_scraping(start_page: int, end_page: int):
    tasks = create_scraper_tasks(start_page, end_page)
    return {"task_ids": tasks}

@app.get("/results/{task_id}")
async def get_results(task_id: str):
    task_result = AsyncResult(task_id)
    if task_result.state == 'SUCCESS':
        logger.info(f"Task {task_id} completed successfully.")
        return {"status": task_result.state, "result": task_result.result}
    elif task_result.state == 'FAILURE':
        logger.error(f"Task {task_id} failed with error: {task_result.result}")
        return {"status": task_result.state, "result": str(task_result.result)}
    return {"status": task_result.state}

@app.get("/results")
async def get_all_results(task_ids: str):
    task_ids = task_ids.split(',')
    results = []
    for task_id in task_ids:
        task_result = AsyncResult(task_id)
        if task_result.state == 'SUCCESS':
            results.append({"task_id": task_id, "status": task_result.state, "result": task_result.result})
        elif task_result.state == 'FAILURE':
            results.append({"task_id": task_id, "status": task_result.state, "result": str(task_result.result)})
        else:
            results.append({"task_id": task_id, "status": task_result.state})
    return {"results": results}

@app.post("/save_results/")
async def save_results(task_ids: str):
    task_ids = task_ids.split(',')
    all_products = []
    for task_id in task_ids:
        task_result = AsyncResult(task_id)
        if task_result.state == 'SUCCESS':
            all_products.extend(task_result.result)  # Directly extend with the result list
        else:
            logger.warning(f"Task {task_id} did not complete successfully. State: {task_result.state}")
    with open("scraped_data.json", "w") as f:
        json.dump(all_products, f)
    logger.info(f"Data saved successfully. Total items: {len(all_products)}")
    return {"message": "Data saved successfully", "data_count": len(all_products)}

@app.get("/view_data/")
async def view_data():
    try:
        with open("scraped_data.json", "r") as f:
            data = json.load(f)
        return {"data": data}
    except FileNotFoundError:
        logger.error("No data found. Please run the scrapers first.")
        return {"error": "No data found. Please run the scrapers first."}
