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
          You are a realstate agent, helping user find the best realstate property.
          
          Generate your response by following the steps below:
          
          1. Attachment Information: Exclude any attachment details mentioned in the property description from your response.
          2. Alternative Options: If the data provides additional options, proactively recommend these to the user.
          3. Description Conciseness: Ensure property descriptions are concise yet comprehensive. Focus on key details to provide a clear overview.
          4. Price Formatting:
              - Always present prices in PHP (Philippine Peso).
              - Omit decimal points when the price ends in .0 or .00.
          5. User Guidance for Specificity: When providing property information, advise the user on how they can refine their query for more targeted results. 
             Encourage specificity in their requests.
          6. Queries unrelated to real estate should be answered by guiding the user back to real estate-related inquiries or providing a brief, polite response 
             indicating the inability to assist with non-real estate questions.
        
          CONTEXT:
           
          {context}

          USER QUERY: {question}

          This is an example of a response a user must see:

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
          
          {format_instructions}        
          """

        system_suggestion_schema = ResponseSchema(
            name="system_suggestion",
            description="""This schema defines the structure for the AI's property suggestion, formatted in markdown for clarity and readability. It includes reasons for the recommendation, 
            ensuring the user understands why this particular property is suggested based on their query and preferences."""
        )

        listing_url_schema = ResponseSchema(
            name="listing_url",
            description="A URL pointing directly to the detailed page of the warehouse listing. Leave this field blank if there is no property recommendation."
        )

        listing_city_schema = ResponseSchema(
            name="listing_city",
            description="The city where the warehouse is located, helping to filter listings by geographical preference. Leave this field blank if there is no property recommendation."
        )

        listing_type_schema = ResponseSchema(
            name="listing_type",
            description="Specifies whether the warehouse is for rent or for sale, catering to different user needs. Leave this field blank if there is no property recommendation."
        )

        listing_price_schema = ResponseSchema(
            name="listing_price",
            description="""The price of the warehouse listing in PHP, formatted according to the guidelines (e.g., omitting decimal points when price ends in .0 or .00). Leave this field blank 
            if there is no property recommendation."""
        )

        listing_markdown_formatted_schema = ResponseSchema(
            name="listing_markdown_formatted",
            description="""A markdown-formatted response that includes all the essential details of the warehouse listing, ensuring clarity and readability. Leave this field blank if there is no 
            property recommendation."""
        )

        no_listing_found_message_schema = ResponseSchema(
            name="no_listing_found_message",
            description="Message to be displayed when no property related to the user's query is found in the given context."
        )
        response_schemas = [
            system_suggestion_schema,
            listing_url_schema,
            listing_city_schema,
            listing_type_schema,
            listing_price_schema,
            listing_markdown_formatted_schema,
            no_listing_found_message_schema
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
            chunk_size=500,
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

        query = "Any warehouse property in makati?"

        advance_message = advance_prompt.format_messages(
            context=from_vector,
            question=query,
            format_instructions=format_instruction
        )

        print(advance_message[0].content)

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
