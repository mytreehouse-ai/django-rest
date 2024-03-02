from logging import getLogger
from django.db import models
from domain.models.base_model import BaseModel

logger = getLogger(__name__)


class ScrapyJobModel(BaseModel):
    """
    ScrapyJobModel stores information about web scraping jobs managed by Scrapy.

    Each instance of this model represents a single scraping job, including its
    unique identifier, the target domain, current status, and other relevant details.

    Attributes:
        id (AutoField): The primary key for the Scrapy job.
        job_id (CharField): A unique identifier for the scraping job.
        domain (URLField): The target URL domain where the scraping job is executed.
        status (CharField): The current status of the scraping job (e.g., 'running', 'completed').
        attempts (IntegerField): The number of execution attempts for the scraping job.
        status_url (URLField): A URL to check the current status of the scraping job.
        supposed_to_run_at (DateTimeField): The scheduled start time for the scraping job.
        is_processed (BooleanField): Flag indicating whether the job has been processed.
        finished_processed_at (DateTimeField): The timestamp when the job processing was completed.
        html_code (TextField): The raw HTML code retrieved by the scraping job, if applicable.
    """

    id = models.AutoField(
        primary_key=True
    )
    job_id = models.CharField(
        max_length=100,
        unique=True,
        blank=False
    )
    domain = models.URLField(
        blank=False,
        null=True
    )
    status = models.CharField(
        max_length=100,
        default="running"
    )
    attempts = models.IntegerField(
        default=0
    )
    status_url = models.URLField(
        blank=False,
        null=True
    )
    supposed_to_run_at = models.DateTimeField(
        null=True,
        blank=True
    )
    single_page = models.BooleanField(
        default=False,
    )
    is_multi_page_processed = models.BooleanField(
        default=False
    )
    is_single_page_processed = models.BooleanField(
        default=False
    )
    finished_processed_at = models.DateTimeField(
        null=True,
        blank=True
    )
    failed_reason = models.TextField(
        null=True
    )
    html_code = models.TextField(
        blank=False,
        null=True
    )

    def __str__(self) -> str:
        """
        Returns the domain of the Scrapy job as its string representation.

        Returns:
            str: The domain URL of the Scrapy job.
        """
        return self.domain

    class Meta:
        db_table = "scrapy_jobs"
        verbose_name = "Scrapy job"
        verbose_name_plural = "Scrapy jobs"
        ordering = ["-supposed_to_run_at"]
