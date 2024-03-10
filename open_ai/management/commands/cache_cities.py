from logging import getLogger
from django.core.management.base import BaseCommand

from open_ai.tasks import update_available_cities_for_ai_context

logger = getLogger(__name__)


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):
        update_available_cities_for_ai_context()
