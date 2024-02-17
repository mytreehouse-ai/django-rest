import os
from logging import getLogger
from celery import shared_task
from django.utils import timezone

logger = getLogger(__name__)


@shared_task()
def scraperapi_job_checker_task():
    pass


@shared_task()
def lamudi_scraper_task():
    pass
