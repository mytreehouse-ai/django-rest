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

        pg_vector = apollo_exporation_service.pg_vector(
            collection_name="property_listings"
        )

        documents = apollo_exporation_service.get_text_chunks_langchain(
            text="""
            4. [Cold Storage Warehouse in Cebu for Rent, 400sqm P250,000](https://www.myproperty.ph/cold-storage-warehouse-in-cebu-for-rent-400sqm-250000.html)
            - Listing type: For Rent
            - Current Price: Php 250,000
            - Lot Area: 400 sqm
            - Address: Mandaue City, Cebu
            - Longitude: 123.9603
            - Latitude: 10.3236
            - Description: 
                - Equipped with state-of-the-art cooling systems
                - 24/7 operation capability
                - Strategically located near ports
            """
        )

        # assistant = apollo_exporation_service.assistant(
        #     query="My budget is around 100k?",
        #     thread_id="sk_12345123123"
        # )

        stored_document = pg_vector.add_documents(documents=documents)

        print(stored_document)

        # print(json.dumps(assistant, indent=4))
