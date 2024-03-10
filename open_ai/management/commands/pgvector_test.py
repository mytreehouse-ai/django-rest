import os
import json
from logging import getLogger
from django.core.management.base import BaseCommand
from django.core.cache import cache
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

        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        ai_instruction_advance = """
            You are a real estate agent helping users find the best real estate property. Generate your response by following the steps below:

                1. Attachment Information: Exclude any attachment details mentioned in the property description from your response.
                
                2. Alternative Options: If the data provides additional options, proactively recommend these to the user.
                
                3.Description Conciseness: Ensure property descriptions are concise yet comprehensive. Focus on key details to provide a clear overview. 
                  Use bullet points or a structured format to improve readability.
                  
                4. Price Formatting:
                    - Always present prices in PHP (Philippine Peso).
                    - Omit decimal points when the price ends in .0 or .00.
                    - Format prices with commas for thousands separators (e.g., Php 1,500,000).
                   
                5. User Guidance for Specificity:
                    - When providing property information, advise the user on how they can refine their query for more targeted results.
                    - Encourage specificity in their requests by suggesting relevant filters or criteria (e.g., location, property type, price range, number of bedrooms/bathrooms).
                    - Provide examples of how users can phrase their queries to get more accurate results.
                   
                6. Off-topic Queries:
                    - If a user's query is unrelated to real estate, guide them back to real estate-related inquiries.
                    - Provide a brief, polite response indicating the inability to assist with non-real estate questions.
                    - Suggest alternative resources or platforms that may be more suitable for their non-real estate needs.
                  
                7. Property availability by places or city:
                    - If a user asks about the places or cities currently available in your [PLACES/CITIES AVAILABLE], provide a helpful response.
                    - Instead of listing all available cities, select 5 representative cities from the [PLACES/CITIES AVAILABLE] to present to the user.
                    - Present the selected cities in a clear and organized manner, such as a bullet-point list or a comma-separated string.
                    - After listing the 5 cities, ask the user if any of these locations match their preferences or if they have a specific place in mind.
                    - Encourage the user to provide more details about their preferred location, such as a specific neighborhood, district, or proximity to certain landmarks or amenities.
                    - If no places or cities are found in the [PLACES/CITIES AVAILABLE], inform the user and suggest alternative ways to explore available properties.
            
            Here are the places and cities where we currently have properties available in our database:
            
            PLACES/CITIES AVAILABLE: {available_cities}

            You can use these locations as a starting point for your property search. Feel free to specify your preferred location, along with other criteria like property 
            type, price range, and desired amenities,
                  
            REALSTATE PROPERTIES: {realstate_properties}

            USER QUERY: {question}

            Example of a response:
            [Commercial Storage Warehouse for Lease Makati near kalayaan 327sqm P150,000](https://www.myproperty.ph/commercial-storage-warehouse-for-lease-makati-near-169192747861.html)
            - Listing type: For Rent
            - Current Price: Php 150,000
            - Lot Area: 300 sqm
            - Address: Olympia, Makati
            - Longitude: 121.01316
            - Latitude: 14.57087
            - Description:
                - Warehouse Storage Commissary for Lease Makati
                - 2 months deposit, 2 months advance
                - Minimum lease of 2 years
                - As-is where-is
            
            To find more suitable properties, you can refine your search by specifying:

            - Desired location (e.g., specific city, neighborhood, or proximity to landmarks)
            - Property type (e.g., residential, commercial, industrial)
            - Price range
            - Required amenities or features
            
            Feel free to provide more details about your preferences to help me find the best properties for you.

            {format_instructions}       
          """

        ai_suggestion_schema = ResponseSchema(
            name="ai_suggestion",
            description="""
            For property suggestions, the response should include:
                - A brief overview of the suggested property and its key features
                - Reasons for the recommendation based on the user's query and preferences
                - Pros and cons of the property (if applicable)
                - Any additional insights or advice related to the suggestion
                - Follow-up questions to the user to promote a more engaging and personalized property
            search experience, such as:
                - Seeking clarification on the user's preferences or requirements
                - Suggesting additional filters or criteria to refine the search
                - Offering alternative options or recommendations based on the user's input
                - Encouraging the user to provide more details for a more accurate property match
            For location-related queries (e.g., available cities or places), the response should include:
                - A clear and concise list of the available cities or places in the database
                - Instructions on how the user can utilize this information to refine their property search
                - Encouragement for the user to provide more specific criteria for a more targeted search
                - An offer to assist the user further with any other questions or requirements
                - Follow-up questions to the user to gather more information about their preferred location, such as:
                    - Asking if any of the listed locations match their preferences
                    - Inquiring if they have a specific place or neighborhood in mind
                    - Encouraging them to provide more details about their ideal location
            If no suitable properties are found or if the database does not contain any locations matching the user's query, the response should:
                - Inform the user that no matching results were found
                - Suggest alternative locations or property types that the user might consider
                - Provide guidance on how the user can modify their search criteria for better results
                - Assure the user that the AI is ready to help with any further inquiries or requirements
                - Ask follow-up questions to better understand the user's needs and preferences, such as:
                    - Inquiring about their budget range or desired amenities
                    - Suggesting related locations or property types that might interest them
                    - Encouraging them to provide more context about their search criteria
                    
                Additionally, include a friendly and informative message when no suitable listings are found:
                    - Acknowledge that no properties matching the user's query were found within the given context
                    - Suggest alternative search criteria or related property types that the user might explore
                    - Encourage the user to modify their query or preferences for better results
                    - Provide guidance on how to refine the search for more relevant listings
                    - Assure the user that the AI is ready to assist with any further inquiries
            """
        )

        listing_url_schema = ResponseSchema(
            name="listing_url",
            description="A direct URL to the detailed page of the recommended property listing. If no suitable property is found, leave this field blank."
        )

        listing_city_schema = ResponseSchema(
            name="listing_city",
            description="""
            The city where the recommended property is located. This information helps users filter listings based on their preferred geographical area. 
            If no suitable property is found, leave this field blank.
            """
        )

        listing_type_schema = ResponseSchema(
            name="listing_type",
            description="""
            Specifies whether the recommended property is available for rent or sale, catering to different user requirements. 
            If no suitable property is found, leave this field blank.
            """
        )

        listing_price_schema = ResponseSchema(
            name="listing_price",
            description="""
                The price of the recommended property listing in PHP. Ensure that the price is formatted according to the guidelines:
                    - Omit decimal points when the price ends in .0 or .00
                    - Use commas as thousands separators (e.g., Php 1,500,000)
                If no suitable property is found, leave this field blank.
            """
        )

        listing_markdown_formatted_schema = ResponseSchema(
            name="listing_markdown_formatted",
            description="""
                A markdown-formatted response that presents all the essential details of the recommended property listing. 
                The response should be structured and easily readable, including:
                    - Property title
                    - Key features and amenities
                    - Location details
                    - Price and payment terms
                    - Contact information or next steps
                If no suitable property is found, leave this field blank.
            """
        )

        response_schemas = [
            ai_suggestion_schema,
            listing_url_schema,
            listing_city_schema,
            listing_type_schema,
            listing_price_schema,
            listing_markdown_formatted_schema,
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

        query = "Any warehouse located in tagaytay?"

        retriever = store.as_retriever()
        relevant_documents = retriever.get_relevant_documents(query=query)
        realstate_properties = [
            data.page_content for data in relevant_documents
        ]

        # print(realstate_properties)

        # print(json.dumps(page_contents, indent=4))

        available_cities = cache.get("open_ai:cities_context")

        advance_message = advance_prompt.format_messages(
            available_cities=available_cities,
            realstate_properties=realstate_properties,
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
