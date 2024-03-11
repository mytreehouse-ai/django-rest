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
            query="warehouse in taguig city?",
            collection_name="mytreehouse_vectors",
            thread_id="sk_sssssssdsdsds"
        )

        print(json.dumps(assistant, indent=4))
