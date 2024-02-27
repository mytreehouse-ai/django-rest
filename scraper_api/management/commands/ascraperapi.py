import os
import logging
import requests
from django.core.management.base import BaseCommand

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
        """
        The main entry point for the command. It constructs the payload and sends the POST request.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments.

        Returns:
            str: The JSON response from the API or an error message.
        """
        # Construct the payload with the necessary parameters for the API request
        payload = {
            # API key for ScraperAPI, fetched from environment variables
            "apiKey": os.environ.get("SCRAPER_API_KEY"),
            "url": "https://www.lamudi.com.ph/condominium/buy/?page=1",  # The URL to scrape
            "callback": {
                "type": "webhook",  # The type of callback, in this case, a webhook
                # The callback URL where the results will be sent
                "url": f"{os.environ.get('DJANGO_API_URL')}/scrapy-jobs/webhook/finished-job"
            }
        }

        # Define the endpoint URL for ScraperAPI where the job will be created
        endpoint = "https://async.scraperapi.com/jobs"

        # Send the POST request to the ScraperAPI with the payload and headers
        response = requests.post(
            endpoint,
            json=payload,
            headers={
                "Content-Type": "application/json"
            }
        )

        # Attempt to parse the response as JSON and handle any parsing errors
        try:
            response_json: CreateScrapyJobSerializer = response.json()

            print(response_json.get("id"))
        except ValueError:
            # Log the error if the response is not a valid JSON
            logger.error("Failed to parse response as JSON.")
            response_json = "Invalid JSON response"

        # Check the status code of the response and log the result
        if response.status_code == 200:
            # Log the success message with the response if the status code is 200
            logger.info(
                f"Scraping job started successfully. Response: {response_json}"
            )
        else:
            # Log the error with the status code and response if the status code is not 200
            logger.error(
                f"Failed to start scraping job. Status code: {response.status_code}, Response: {response_json}"
            )

        # Return the JSON response or the error message as a string
        return str(response_json)
