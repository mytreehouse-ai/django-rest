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

        history = apollo_exporation_service.message_history(
            session_id="sk_asdasd123asd"
        )

        # history.add_user_message(message="Hi!")

        # history.add_ai_message(message="Hello")

        for message in history.messages:
            jayson = message.to_json()
            kwargs_ni_jayson = jayson.get("kwargs")

            print(
                f"{kwargs_ni_jayson.get('type')}: {kwargs_ni_jayson.get('content')}"
            )
