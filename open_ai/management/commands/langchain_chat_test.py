import os
import logging
from django.core.management.base import BaseCommand
from ...services.open_ai_services import OpenAILocalServices


logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Run the OpenAI chain with a supplied question"

    def add_arguments(self, parser):
        parser.add_argument('question', type=str, help='The question to send to the OpenAI service')

    def handle(self, *args, **options):
        question = options['question']
        open_ai_services = OpenAILocalServices(api_key=os.environ.get("OPENAI_API_KEY"))
        open_ai_services.run_chain(question)
        # Implementing a new line as per instructions
        self.stdout.write("\n\n")
        self.stdout.write(self.style.SUCCESS('Successfully got response from OpenAI service'))
        return None

# python manage.py langchain_chat_test "Is there any property available in Makati or Valenzuela that has an area of at least 100 square meters?"
# python manage.py langchain_chat_test "Can you please provide me with two options for large warehouses that are currently available?"
# python manage.py langchain_chat_test "Is there a warehouse located near Taguig that is at least 100 sqm in size?"