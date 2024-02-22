import os
import json
from typing import List
from logging import getLogger
from django.utils import timezone
from django.core.cache import cache

from ..models.scrapy_job_model import ScrapyJobModel
from ..models.scrapy_web_model import ScrapyWebModel

logger = getLogger(__name__)


class ScrapyJobService:

    def get_all_scrapy_web(self) -> List[ScrapyWebModel]:
        """
        Retrieves all ScrapyWebModel instances from the database.

        This method queries the database for all instances of ScrapyWebModel, which store the URLs to be scraped by the Scrapy service, and returns them. It is essential for identifying all the target URLs that the Scrapy service will process.

        Returns:
            QuerySet: A QuerySet containing all instances of ScrapyWebModel, representing all URLs to be scraped.
        """

        cache_result = cache.get("scrapy_webs")

        if cache_result:
            return json.loads(cache_result)

        scrapy_webs = ScrapyWebModel.objects.all()

        cache.set(
            key="scrapy_webs",
            value=json.dumps(
                scrapy_webs
            ),
            timeout=None
        )

        return scrapy_webs

    def job_checker():
        running_jobs = ScrapyJobModel.objects.filter(status="running")[:10]

    def create_job(self, **kwargs):
        """
        Creates a new Scrapy job in the database.

        This method takes keyword arguments that correspond to the fields of the ScrapyJobModel
        and creates a new instance of ScrapyJobModel with these fields.

        Args:
            **kwargs: Variable length keyword arguments. Expected to contain all necessary fields
            for creating a ScrapyJobModel instance.

        Returns:
            ScrapyJobModel: The newly created ScrapyJobModel instance.
        """
        return ScrapyJobModel.objects.create(**kwargs)

    def update_job(self, job_id: str, attempts: int, status: str, html_code: str | None, failed_reason: str | None) -> None:
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
            job = ScrapyJobModel.objects.get(id=job_id)
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
