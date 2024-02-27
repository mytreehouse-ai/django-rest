import os
import logging
from django.core.management.base import BaseCommand
from django_celery_beat.models import IntervalSchedule, PeriodicTask
import zoneinfo

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    A Django management command intended to be run periodically to ensure that a specific
    Celery beat schedule is set up in the database. This command creates an IntervalSchedule
    to run every five minutes if it does not already exist. It then ensures a PeriodicTask
    is associated with this schedule to execute the 'scraper_api.tasks.lamudi_scraper' task.

    The command outputs the details of the IntervalSchedule and PeriodicTask to the console,
    indicating whether each was created or retrieved from the existing entries.
    """

    def handle(self, *args, **options):
        # Attempt to retrieve an IntervalSchedule that runs every 5 minutes. If it doesn't exist, create a new one.
        every_five_minutes, created = IntervalSchedule.objects.get_or_create(
            every=5,  # The interval in minutes
            period=IntervalSchedule.MINUTES  # The type of period, in this case, minutes
        )
        # Create or retrieve a PeriodicTask linked to the above IntervalSchedule.
        periodic_task, task_created = PeriodicTask.objects.get_or_create(
            interval=every_five_minutes,
            name="Scraper API Lamudi Scraper",
            task="scraper_api.tasks.lamudi_scraper"
        )

        # Print the details of the IntervalSchedule and PeriodicTask to the console.
        print(every_five_minutes, created)
        print(periodic_task, task_created)
