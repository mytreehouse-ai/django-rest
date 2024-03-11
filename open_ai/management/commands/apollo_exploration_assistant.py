import os
import json
from logging import getLogger
from django.core.management.base import BaseCommand

from open_ai.services.apollo_exploration.service import ApolloExplorationService

logger = getLogger(__name__)


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):
        apollo_exporation_service = ApolloExplorationService(
            api_key=os.getenv("OPENAI_API_KEY")
        )

        assistant = apollo_exporation_service.assistant(
            query="Condominium that is near uptown mall?",
            collection_name="property_listings",
            thread_id="sk_123abcdefg45678910"
        )

        print(json.dumps(assistant, indent=4))
