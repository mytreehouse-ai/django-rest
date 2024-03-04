import os
import json
from logging import getLogger
from django.core.management.base import BaseCommand
from openai import OpenAI
from langchain.vectorstores.pgvector import PGVector
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain_community.document_loaders import TextLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = getLogger(__name__)


class Command(BaseCommand):

    help = ""

    def handle(self, *args, **options):
        OpenAI.api_key = os.getenv("OPENAI_API_KEY")
        pg_host = os.getenv("POSTGRES_HOST")
        pg_user = os.getenv("POSTGRES_USERNAME")
        pg_pass = os.getenv("POSTGRES_PASSWORD")
        pg_db = os.getenv("POSTGRES_DATABASE")
        ssl_mode = "require" if os.getenv(
            "POSTGRES_SSL_ON") == "1" else "disable"

        connection_string = f"postgresql+psycopg2://{pg_user}:{pg_pass}@{pg_host}:5432/{pg_db}?sslmode={ssl_mode}"
        collection_name = "mytreehouse_vectors"

        llm = ChatOpenAI(
            model="gpt-3.5-turbo-0125",
            temperature=0.0
        )

        embeddings = OpenAIEmbeddings()

        ai_instruction_advance = """
          Listings: {context}

          Question: {question}

          When responding to property inquiries, please adhere to the following guidelines:

          1. Attachment Information: Exclude any attachment details mentioned in the property description from your response.
          2. Alternative Options: If the data provides additional options, proactively recommend these to the user.
          3. Description Conciseness: Ensure property descriptions are concise yet comprehensive. Focus on key details to provide a clear overview.
          4. For queries unrelated to warehouse, always treat them as FAQs and provide unlimited responses for industrial FAQs and always respond with complete details.
          5. Price Formatting:
              - Always present prices in PHP (Philippine Peso).
              - Omit decimal points when the price ends in .0 or .00.
          6. User Guidance for Specificity: When providing property information, advise the owner on how they can refine their query for more targeted results. Encourage specificity in their requests.
          7. If a keyword is highly similar to the description, include it in the recommendation.
          8. It is important to be specific about the location. If the user asks for Makati, only provide the Makati warehouse location, and if they ask for Taguig, provide the Taguig location, and so on.

          This is an example of a single response a user wants to see supply this into the listing_markdown_formatted_response property and should be a markdown:

          ```example start
          [Commercial Storage Warehouse for Lease Makati near kalayaan 327sqm P150,000](https://www.myproperty.ph/commercial-storage-warehouse-for-lease-makati-near-169192747861.html)
              - Listing type: For Rent
              - Current Price: Php 150,000
              - Lot Area: 300 sqm
              - Address: Olympia, Makati
              - Longitude: 121.01316
              - Latitude: 14.57087
              - Description: 
                  - Warehouse Storage Commissary for Lease Makati
                  - 2 months deposit 2 months advance
                  - Minimum lease 2 years
                  - As-is where-is
          example end```
          
          {format_instructions}
          
          When responding to a prompt unrelated to warehouse properties, always reply as a friendly assistant. Let the user know that you only cater Industrial property related to warehouse.
          """

        listing_url = ResponseSchema(
            name="listing_url",
            description="The URL of the listing, providing a direct link to the warehouse's detailed page. Omitted if 'no_listing_found_message' is not empty."
        )

        listing_city = ResponseSchema(
            name="listing_city",
            description="The city where the warehouse is located, helping to filter listings by geographical preference. Omitted if 'no_listing_found_message' is not empty."
        )

        listing_type = ResponseSchema(
            name="listing_type",
            description="Specifies whether the warehouse is for rent or for sale, catering to different user needs. Omitted if 'no_listing_found_message' is not empty."
        )

        listing_price = ResponseSchema(
            name="listing_price",
            description="The price of the warehouse listing in PHP, formatted according to the guidelines (e.g., omitting decimal points when price ends in .0 or .00). Omitted if 'no_listing_found_message' is not empty."
        )

        listing_markdown_formatted_response = ResponseSchema(
            name="listing_markdown_formatted_response",
            description="A markdown-formatted response that includes all the essential details of the warehouse listing, ensuring clarity and readability. Omitted if 'no_listing_found_message' is not empty."
        )

        no_listing_found_message = ResponseSchema(
            name="no_listing_found_message",
            description="Message to be displayed when no property related to the user's query is found. Omitted if listing_url, listing_city, listing_type, listing_price, and listing_markdown_formatted_response are not empty."
        )
        response_schemas = [
            listing_url,
            listing_city,
            listing_type,
            listing_price,
            listing_markdown_formatted_response,
            no_listing_found_message
        ]

        output_parser = StructuredOutputParser.from_response_schemas(
            response_schemas=response_schemas
        )

        format_instruction = output_parser.get_format_instructions()

        advance_prompt = ChatPromptTemplate.from_template(
            template=ai_instruction_advance
        )

        loader = TextLoader(
            "open_ai/documents/warehouse_listings.txt",
            encoding="utf-8"
        )

        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            # Adjusted for more granular splitting, considering the detailed nature of warehouse listings.
            chunk_size=500,
            # Reduced overlap to balance between context preservation and redundancy.
            chunk_overlap=50
        )

        texts = text_splitter.split_documents(documents=documents)

        store = PGVector(
            embedding_function=embeddings,
            collection_name=collection_name,
            connection_string=connection_string,
        )

        # store.add_documents(documents=texts)

        from_vector = store.as_retriever()

        query = "Any available in taguig city?"

        advance_message = advance_prompt.format_messages(
            context=from_vector,
            question=query,
            format_instructions=format_instruction
        )

        response = llm.invoke(advance_message)

        output_dict = output_parser.parse(response.content)

        print(json.dumps(output_dict, indent=4))

        # similarity = store.similarity_search_with_score(query=query)

        """
            select document (embedding <=> '[-0.2372847.....]') as cosine_distance
            from langchain_pg_embedding
            order by cosine_distance
            limit 2
        """
