
# Scraper Project

## Prerequisites

1. **Redis**:
   - Redis is used as a message broker for Celery.
   - Installation instructions can be found on the [Redis website](https://redis.io/download).

2. **MongoDB**:
   - MongoDB is used as the database to store scraped data.
   - Installation instructions can be found on the [MongoDB website](https://www.mongodb.com/try/download/community).

3. **Python Packages**:
   - You need to install the required Python packages. Install the packages using `requirements.txt`.

## Setup

1. **Clone the repository**:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```


2. **Install required packages**:
   ```
   pip install -r requirements.txt
   ```

3. **Start Redis**:
   Follow the instructions on the Redis website to start the Redis server.

4. **Start MongoDB**:
   Follow the instructions on the MongoDB website to start the MongoDB server.

## Running the Project

1. **Start Redis**:
   ```
   redis-server
   ```


2. **Start Celery workers**:
   ```
   celery -A scraper1 worker --loglevel=info -P eventlet -Q scraper1_queue
   celery -A scraper2 worker --loglevel=info -P eventlet -Q scraper2_queue
   celery -A scraper3 worker --loglevel=info -P eventlet -Q scraper3_queue
   ```

3. **Start the FastAPI server for the main application**:
   ```
   uvicorn main:app --reload --port 8000
   ```

4. **Start the FastAPI server for the database**:
   ```
   uvicorn database:app --reload --port 8004
   ```

## Usage

1. Open your browser and navigate to `http://localhost:8000`.
2. Click the "Start Scrapers" button to initiate the scraping process.
3. Once the scraping is complete, click "Load Data" to view the scraped data.
4. Use the dropdown to sort the data by price.
