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

        get_conversation_history = apollo_exporation_service.get_message_history(
            thread_id="sk_asdasd123asd"
        )

        # history.add_user_message(message="Hi!")

        # history.add_ai_message(message="Hello")

        conversation_history = """"""

        if len(get_conversation_history.messages) == 0:
            conversation_history = "This is a new query no conversation history at the moment"
        else:
            for message in get_conversation_history.messages:
                message_json = message.to_json()
                message_data = message_json.get("kwargs")
                message_type = message_data.get('type')
                message_content = message_data.get('content')
                conversation_history += f"{message_type.title()}: {message_content}\n"

        print(conversation_history)
