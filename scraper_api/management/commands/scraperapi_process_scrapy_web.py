import os
import logging
import requests
from time import sleep
from django.core.management.base import BaseCommand

from ...serializers.create_scrapy_job_serializer import CreateScrapyJobSerializer
from scraper_api.services.scraperapi_service import ScrapyJobService
from scraper_api.models.scrapy_job_model import ScrapyJobModel

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Django management command to send a POST request to ScraperAPI to initiate a scraping job.

    This command is designed to automate the process of initiating scraping jobs through the ScraperAPI. 
    It iterates over all configured scraping websites, constructing and sending a POST request for each page 
    that needs to be scraped. The request includes a payload with the API key, the target URL with the page 
    number, and a callback URL for webhook notifications upon job completion.

    The response from the ScraperAPI is processed to extract job details, which are then used to create a 
    new scraping job record in the database. Errors during the request or response handling are logged 
    appropriately.

    Attributes:
        help (str): Provides a brief description of the command's purpose.

    Methods:
        handle(*args, **options): The main entry point for the command. It retrieves all scraping website 
        configurations, constructs the necessary requests to the ScraperAPI, and handles the responses.
    """

    help = "Sends a POST request to ScraperAPI to start a scraping job."

    def handle(self, *args, **options):
        scrapy_webs = ScrapyJobService.get_all_scrapy_web()

        for scrapy_web in scrapy_webs:
            for i in range(1, scrapy_web.page_number + 1):
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
                    ScrapyJobModel.objects.update_or_create(
                        domain=response_json.get("url", None),
                        defaults={
                            "job_id": response_json.get("id", None),
                            "status": response_json.get("status", None),
                            "attempts": response_json.get("attempts", None),
                            "status_url": response_json.get("status_url", None),
                            "supposed_to_run_at": response_json.get("supposedToRunAt", None)
                        }
                    )
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

                sleep(0.5)
