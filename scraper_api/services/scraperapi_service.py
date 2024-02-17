import os
from logging import getLogger
from django.utils import timezone

from ..models.scrapy_job_model import ScrapyJobModel

logger = getLogger(__name__)


class ScrapyJobService:

    def job_checker():
        running_jobs = ScrapyJobModel.objects.filter(status="running")[:10]

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
            job = None
