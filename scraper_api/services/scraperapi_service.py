import os
import requests
from typing import List, Optional
from logging import getLogger
from django.utils import timezone

from ..models.scrapy_job_model import ScrapyJobModel
from ..models.scrapy_web_model import ScrapyWebModel

logger = getLogger(__name__)


class ScrapyJobService:

    @staticmethod
    def scraper_api(scrapy_web: str):
        payload = {
            "apiKey": os.environ.get("SCRAPER_API_KEY"),
            "url": scrapy_web,
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

        return response

    @staticmethod
    def get_all_scrapy_web() -> List[ScrapyWebModel]:
        """
        Retrieves all ScrapyWebModel instances from the database.

        This method queries the database for all instances of ScrapyWebModel, which store the URLs to be scraped by the Scrapy service, and returns them. 
        It is essential for identifying all the target URLs that the Scrapy service will process.

        Returns:
            List[ScrapyWebModel]: A list containing all instances of ScrapyWebModel, representing all URLs to be scraped.
        """

        scrapy_webs = ScrapyWebModel.objects.filter(is_active=True)

        return list(scrapy_webs)

    @staticmethod
    def get_all_scrapy_job_for_task() -> List[ScrapyJobModel]:
        """
        Fetches a limited list of ScrapyJobModel instances representing completed, unprocessed scraping jobs from the database.

        This method is designed to retrieve a subset of ScrapyJobModel records that match specific criteria: the jobs must be marked as 'finished', 
        not yet processed, and optionally filtered to include only jobs that either targeted a single page or multiple pages, based on the 'single_page' parameter. 
        This functionality is particularly useful for batch processing or reviewing the outcomes of recent scraping activities.

        Args:
            single_page (Optional[bool]): A flag to filter the jobs based on whether they were for a single page or not. Defaults to False.

        Returns:
            List[ScrapyJobModel]: A list of up to 10 ScrapyJobModel instances that meet the specified criteria.
        """
        return ScrapyJobModel.objects.filter(is_multi_page_processed=False, single_page=False, html_code__isnull=False).order_by('-updated_at')[:10]

    @staticmethod
    def get_all_scrapy_job_for_selenium():
        """
        Retrieves all ScrapyJobModel instances from the database without any filtering.

        This method queries the database for all instances of ScrapyJobModel, which represent individual 
        scraping jobs that have been initiated or completed using Selenium. It is crucial for monitoring, 
        managing, and analyzing the performance and outcomes of the scraping jobs initiated by Selenium.

        Returns:
            QuerySet[ScrapyJobModel]: A QuerySet containing all instances of ScrapyJobModel.
        """
        return ScrapyJobModel.objects.filter()

    @staticmethod
    def get_scrapy_job(job_id: int) -> ScrapyJobModel:
        """
        Retrieves a single ScrapyJobModel instance from the database by its job ID.

        This method queries the database for a ScrapyJobModel instance by its unique job identifier. It is used
        to fetch detailed information about a specific scraping job, including its status, attempts, and
        other relevant data.

        Args:
            job_id (int): The unique job identifier of the ScrapyJobModel to retrieve.

        Returns:
            ScrapyJobModel: An instance of ScrapyJobModel corresponding to the provided job ID.
        """
        return ScrapyJobModel.objects.get(job_id=job_id)

    @staticmethod
    def create_job(**kwargs):
        """
        Creates a new Scrapy job in the database.

        This method takes keyword arguments that correspond to the fields of the ScrapyJobModel
        and creates a new instance of ScrapyJobModel with these fields. It is defined as a static method
        to allow calling it without an instance of ScrapyJobService. It catches and logs any errors that occur during the creation of a new ScrapyJobModel instance.

        Args:
            **kwargs: Variable length keyword arguments. Expected to contain all necessary fields
            for creating a ScrapyJobModel instance.

        Returns:
            ScrapyJobModel: The newly created ScrapyJobModel instance or None if an error occurred.
        """
        try:
            return ScrapyJobModel.objects.create(**kwargs)
        except Exception as e:
            logger.error(f"Failed to create ScrapyJobModel: {e}")
            return None

    @staticmethod
    def update_job(domain: str, job_id: str, attempts: int, status: str, status_url: str, single_page: Optional[bool] = False, html_code: Optional[str] = None, failed_reason: Optional[str] = None) -> None:
        """
        Updates the details of a specific Scrapy job in the database.

        This method updates the attempts, status, and potentially the html_code and failed_reason
        of a Scrapy job identified by its job_id. It also sets the finished_processed_at timestamp
        to the current time.

        Args:
            job_id (str): The unique identifier of the Scrapy job to update.
            attempts (int): The number of attempts made for the Scrapy job.
            status (str): The new status of the Scrapy job.
            html_code (Optional[str]): The HTML code retrieved by the Scrapy job, if applicable.
            failed_reason (Optional[str]): The reason the Scrapy job failed, if applicable.

        Returns:
            None
        """
        try:
            job = ScrapyJobModel.objects.get(domain=domain)
            job.job_id = job_id
            job.attempts = attempts
            job.status = status
            job.status_url = status_url
            job.single_page = single_page
            job.finished_processed_at = timezone.now()

            update_fields = [
                "job_id",
                "attempts",
                "status",
                "status_url",
                "single_page",
                "finished_processed_at"
            ]

            if html_code is not None:
                job.html_code = html_code
                update_fields.append("html_code")

            if failed_reason is not None:
                job.failed_reason = failed_reason
                update_fields.append("failed_reason")

            job.save(update_fields=update_fields)

        except ScrapyJobModel.DoesNotExist:
            logger.error(f"ScrapyJobModel with id {job_id} does not exist.")
            job = None
