from typing import List
from logging import getLogger
from django.utils import timezone

from ..models.scrapy_job_model import ScrapyJobModel
from ..models.scrapy_web_model import ScrapyWebModel

logger = getLogger(__name__)


class ScrapyJobService:

    def get_all_scrapy_web() -> List[ScrapyWebModel]:
        """
        Retrieves all ScrapyWebModel instances from the database.

        This method queries the database for all instances of ScrapyWebModel, which store the URLs to be scraped by the Scrapy service, and returns them. 
        It is essential for identifying all the target URLs that the Scrapy service will process.

        Returns:
            QuerySet: A QuerySet containing all instances of ScrapyWebModel, representing all URLs to be scraped.
        """

        scrapy_webs = ScrapyWebModel.objects.filter(is_active=True)

        return scrapy_webs

    def get_all_scrapy_job() -> List[ScrapyJobModel]:
        """
        Retrieves all ScrapyJobModel instances from the database.

        This method queries the database for all instances of ScrapyJobModel, which represent individual 
        scraping jobs that have been initiated or completed. It is crucial for monitoring, managing, and 
        analyzing the performance and outcomes of the scraping jobs.

        Returns:
            List[ScrapyJobModel]: A list containing all instances of ScrapyJobModel limited by 5 records, representing all scraping jobs.
        """
        return ScrapyJobModel.objects.filter(status="finished", is_processed=False)[:5]

    def get_scrapy_job(id: int) -> ScrapyJobModel:
        """
        Retrieves a single ScrapyJobModel instance from the database by its ID.

        This method queries the database for a ScrapyJobModel instance by its unique identifier. It is used
        to fetch detailed information about a specific scraping job, including its status, attempts, and
        other relevant data.

        Args:
            id (int): The unique identifier of the ScrapyJobModel to retrieve.

        Returns:
            ScrapyJobModel: An instance of ScrapyJobModel corresponding to the provided ID.
        """
        return ScrapyJobModel.objects.get(id=id)

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

    def update_job(job_id: str, attempts: int, status: str, html_code: str | None, failed_reason: str | None) -> None:
        """
        Updates the details of a specific Scrapy job in the database.

        This method updates the attempts, status, and potentially the html_code and failed_reason
        of a Scrapy job identified by its job_id. It also sets the finished_processed_at timestamp
        to the current time.

        Args:
            job_id (str): The unique identifier of the Scrapy job to update.
            attempts (int): The number of attempts made for the Scrapy job.
            status (str): The new status of the Scrapy job.
            html_code (str | None): The HTML code retrieved by the Scrapy job, if applicable.
            failed_reason (str | None): The reason the Scrapy job failed, if applicable.

        Returns:
            None
        """
        try:
            job = ScrapyJobModel.objects.get(job_id=job_id)
            job.attempts = attempts
            job.status = status
            job.finished_processed_at = timezone.now()
            job.save(
                update_fields=[
                    "attempts",
                    "status",
                    "finished_processed_at"
                ]
            )

            if html_code:
                job.html_code = html_code
                job.save(update_fields=["html_code"])

            if failed_reason:
                job.failed_reason = failed_reason
                job.save(update_fields=["failed_reason"])

        except ScrapyJobModel.DoesNotExist:
            logger.error(f"ScrapyJobModel with id {job_id} does not exist.")
            job = None
