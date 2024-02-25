import os
import requests
from time import sleep
from logging import getLogger
from celery import shared_task
from django.utils import timezone

from .services.scraperapi_service import ScrapyJobService
from .serializers.create_scrapy_job_serializer import CreateScrapyJobSerializer

logger = getLogger(__name__)


@shared_task()
def scraperapi_process_scrapy_web():
    """
    Initiates scraping jobs for each page of every Scrapy web entity.

    This function iterates through all Scrapy web entities retrieved from the database
    and sends a POST request to the ScraperAPI for each page of each Scrapy web entity.
    It constructs a payload containing the API key, the URL to scrape (with page number),
    and a callback webhook URL. After sending the request, it processes the response,
    creating a new Scrapy job in the database with the response data or logs an error
    if the response cannot be parsed as JSON or if the ScraperAPI returns an error status code.
    """
    scrapy_webs = ScrapyJobService.get_all_scrapy_web()

    for scrapy_web in scrapy_webs:
        # Adjusted to include the last page
        for i in range(1, scrapy_web.page_number):
            print(f"{scrapy_web.web_url}/?page={i}")

            payload = {
                "apiKey": os.environ.get("SCRAPER_API_KEY"),
                "url": f"{scrapy_web.web_url}/?page={i}",
                "callback": {
                    "type": "webhook",
                    "url": f"{os.environ.get('DJANGO_API_URL')}/scrapy-jobs/webhook/finished-job"
                }
            }

            endpoint = "https://async.scraperapi.com/jobs"

            response = requests.post(
                endpoint,
                json=payload,
                headers={
                    "Content-Type": "application/json"
                }
            )

            try:
                response_json: CreateScrapyJobSerializer = response.json()
                job = {
                    "job_id": response_json.get("id", None),
                    "domain": response_json.get("url", None),
                    "status": response_json.get("status", None),
                    "attempts": response_json.get("attempts", None),
                    "status_url": response_json.get("status_url", None),
                    "supposed_to_run_at": response_json.get("supposedToRunAt", None)
                }
                ScrapyJobService.create_job(**job)
            except ValueError:
                logger.error("Failed to parse response as JSON.")
                response_json = "Invalid JSON response"
            if response.status_code == 200:
                logger.info(
                    f"Scraping job started successfully. Response: {response_json}"
                )
            else:
                logger.error(
                    f"Failed to start scraping job. Status code: {response.status_code}, Response: {response_json}"
                )

            # Sleep for 2 seconds after each page iteration to avoid overwhelming the server
            sleep(2)


@shared_task()
def scraperapi_job_checker_task():
    pass


@shared_task()
def lamudi_scraper_task():
    pass
