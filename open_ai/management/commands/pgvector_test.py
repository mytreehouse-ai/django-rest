import os
from logging import getLogger
from django.core.management.base import BaseCommand
from langchain.vectorstores.pgvector import PGVector
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.output_parsers import ResponseSchema
from langchain_community.document_loaders import TextLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = getLogger(__name__)


class Command(BaseCommand):

    help = ""

    def handle(self, *args, **options):
        openai_api_key = os.getenv("OPENAI_API_KEY")
        pg_host = os.getenv("POSTGRES_HOST")
        pg_user = os.getenv("POSTGRES_USERNAME")
        pg_pass = os.getenv("POSTGRES_PASSWORD")
        pg_db = os.getenv("POSTGRES_DATABASE")
        ssl_mode = "require" if os.getenv(
            "POSTGRES_SSL_ON") == "1" else "disable"

        connection_string = f"postgresql+psycopg2://{pg_user}:{pg_pass}@{pg_host}:5432/{pg_db}?sslmode={ssl_mode}"
        collection_name = "mytreehouse_vectors"

        llm = ChatOpenAI(
            api_key=openai_api_key,
            model="gpt-3.5-turbo-0125",
            temperature=0.0
        )

        embeddings = OpenAIEmbeddings(api_key=os.getenv("OPENAI_API_KEY"))

        chat_prompt_template_text = """
          Answer the question based only on the following question: {context}

          Question: {question}

          When responding to property inquiries, please adhere to the following guidelines:

          1. Attachment Information: Exclude any attachment details mentioned in the property description from your response.
          2. Alternative Options: If the data provides additional options, proactively recommend these to the user.
          3. Description Conciseness: Ensure property descriptions are concise yet comprehensive. Focus on key details to provide a clear overview.
          4. Warehouse Listings: If the user asks for all available warehouses, we can show 5 examples and prompt the user to specify their interest in a particular warehouse for more detailed information.
          5. For queries unrelated to warehouse, always treat them as FAQs and provide unlimited responses for industrial FAQs and always respond with complete details.
          6. Price Formatting:
              - Always present prices in PHP (Philippine Peso).
              - Omit decimal points when the price ends in .0 or .00.
          7. User Guidance for Specificity: When providing property information, advise the owner on how they can refine their query for more targeted results. Encourage specificity in their requests.
          8. If a keyword is highly similar to the description, include it in the recommendation.
          9. If the user doesn't mention the warehouse, please assume they are looking for one.
          10. It is important to be specific about the location. If the user asks for Makati, only provide the Makati warehouse location, and if they ask for Taguig, provide the Taguig location, and so on.
          10. Markdown Format: All responses should be formatted in markdown for clarity and readability and always target="_blank" when you include a link in your response.

          Follow this response format for warehouse inquiry:

          Listing Title:
          Listing URL:
          Listing type:
          Current Price:
          Lot Area:
          Address:
          Longitude:
          Latitude:
          description:

          This is an example of a single response a user wants to see:

          ```example start
          1. [Commercial Storage Warehouse for Lease Makati near kalayaan 327sqm P150,000](https://www.myproperty.ph/commercial-storage-warehouse-for-lease-makati-near-169192747861.html)
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

          If you have any further questions or need more details about these warehouses, please let me know.
          example end```
          
          When responding to a prompt unrelated to warehouse properties, always reply as a friendly assistant. Let the user know that you only cater Industrial property related to warehouse.
          """

        chat_prompt_template = ChatPromptTemplate.from_template(
            chat_prompt_template_text
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

        store.add_documents(documents=texts)

        retriever = store.as_retriever()

        query = "I need atleast 1200sqm somewhere in bulacan?"

        # similarity = store.similarity_search_with_score(query=query)

        """
            select document (embedding <=> '[-0.2372847.....]') as cosine_distance
            from langchain_pg_embedding
            order by cosine_distance
            limit 2
        """

        chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | chat_prompt_template
            | llm
            | StrOutputParser()
        )

        print(chain.invoke(query))
