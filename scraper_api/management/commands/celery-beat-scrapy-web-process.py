import os
import logging
from django.core.management.base import BaseCommand
from django_celery_beat.models import CrontabSchedule, PeriodicTask
import zoneinfo

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    A Django management command intended to be run periodically to ensure that a specific
    Celery beat schedule is set up in the database. This command creates a CrontabSchedule
    to run every Sunday at 3 AM in the Asia/Manila timezone if it does not already exist.
    It then ensures a PeriodicTask is associated with this schedule to execute the
    'scraper_api.tasks.scraperapi_process_scrapy_web' task.

    The command outputs the details of the CrontabSchedule and PeriodicTask to the console,
    indicating whether each was created or retrieved from the existing entries.
    """

    def handle(self, *args, **options):
        # Create or retrieve a CrontabSchedule for every Sunday at 3 AM.
        every_sunday_at_3am, created = CrontabSchedule.objects.get_or_create(
            minute="0",
            hour="3",
            day_of_week="0",
            day_of_month="*",
            month_of_year="*",
            timezone=zoneinfo.ZoneInfo('Asia/Manila')
        )

        # Create or retrieve a PeriodicTask linked to the above CrontabSchedule.
        periodic_task, task_created = PeriodicTask.objects.get_or_create(
            priority=0,
            crontab=every_sunday_at_3am,
            name="Scraper API Process Scrapy Web",
            task="scraper_api.tasks.scraperapi_process_scrapy_web"
        )

        # Print the details of the CrontabSchedule and PeriodicTask to the console.
        print(every_sunday_at_3am, created)
        print(periodic_task, task_created)
