import os
import logging
import requests
from time import sleep
from django.core.management.base import BaseCommand

from scraper_api.services.scraperapi_service import ScrapyJobService
from ...serializers.create_scrapy_job_serializer import CreateScrapyJobSerializer

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Django management command to send a POST request to ScraperAPI to initiate a scraping job.

    This command constructs a payload with the necessary parameters and sends a POST request
    to the ScraperAPI endpoint. It handles the response and logs the outcome of the request.
    """

    help = "Sends a POST request to ScraperAPI to start a scraping job."

    def handle(self, *args, **options):
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
