import os
import logging
import asyncio
from typing import AsyncIterable
from django.core.management.base import BaseCommand
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.callbacks import AsyncIteratorCallbackHandler

from ...services import MongoDBConnector


logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Run the OpenAI chain with a supplied question"

    def add_arguments(self, parser):
        parser.add_argument('question', type=str, help='The question to send to the OpenAI service')
    
    async def send_message(content: str) -> AsyncIterable[str]:
        callback = AsyncIteratorCallbackHandler()

        model = ChatOpenAI(
            streaming=True,
            verbose=True,
            callbacks=[callback]
        )
        
        # task = asyncio.current_task(
        #     model.agenerate([[]])
        # )

    def handle(self, *args, **options):
        question = options['question']
        mongodb_uri = os.environ.get('MONGODB_URI', None)
        mongodb = MongoDBConnector(mongodb_uri)
        vector_question = self.convert_to_vector(text=question)
        warehouse_data = mongodb.search_vectors(query_vector=vector_question, num_results=25)

        self.stdout.write("\n\n")
        self.stdout.write(self.style.SUCCESS('Successfully got response from OpenAI service'))
        return None
    
    # python manage.py async_langchain_chat_test "Is there any property available in Makati or Valenzuela that has an area of at least 100 square meters?"
# python manage.py async_langchain_chat_test "Can you please provide me with two options for large warehouses that are currently available?"
# python manage.py async_langchain_chat_test "Is there a warehouse located near Taguig that is at least 100 sqm in size?"