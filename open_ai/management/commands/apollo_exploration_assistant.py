import os
import json
from logging import getLogger
from django.core.management.base import BaseCommand

from open_ai.services.apollo_exploration.service import ApolloExplorationService
from open_ai.tasks import update_vector_property_listings

logger = getLogger(__name__)


class Command(BaseCommand):
    help = ""

    def handle(self, *args, **options):
        apollo_exporation_service = ApolloExplorationService(
            api_key=os.getenv("OPENAI_API_KEY")
        )

        # assistant = apollo_exporation_service.assistant(
        #     query="Warehouse with Fire exits?",
        #     collection_name="property_listings",
        #     thread_id="sk_sssssssdsdsds"
        # )

        update_vector_property_listings()

        # print(json.dumps(assistant, indent=4))
