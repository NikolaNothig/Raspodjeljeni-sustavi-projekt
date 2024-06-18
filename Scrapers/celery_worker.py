from celery import Celery

app = Celery('scraper_tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

app.conf.task_routes = {
    'scraper1.scrape1': {'queue': 'scraper1_queue'},
    'scraper2.scrape2': {'queue': 'scraper2_queue'},
    'scraper3.scrape3': {'queue': 'scraper3_queue'},
}
