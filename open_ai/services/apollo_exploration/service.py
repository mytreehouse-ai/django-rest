import os
from typing import List
from logging import getLogger
from openai import OpenAI
from django.core.cache import cache
from langchain.vectorstores.pgvector import PGVector
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.output_parsers import StructuredOutputParser
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.document import Document

from .response_schemas import response_schemas
from .chat_prompts import chat_prompt


logger = getLogger(__name__)


class ApolloExplorationService:
    def __init__(self, api_key: str):
        OpenAI(api_key=api_key)
        self.pg_host = os.getenv("POSTGRES_HOST")
        self.pg_user = os.getenv("POSTGRES_USERNAME")
        self.pg_pass = os.getenv("POSTGRES_PASSWORD")
        self.pg_db = os.getenv("POSTGRES_DATABASE")
        self.pg_port = os.getenv("POSTGRES_PORT")
        self.ssl_mode = "require" if os.getenv(
            "POSTGRES_SSL_ON") == "1" else "disable"
        self.redis_database_url = os.getenv("REDIS_CACHE_URL")
        self.connection_string = f"postgresql+psycopg2://{self.pg_user}:{self.pg_pass}@{self.pg_host}:{self.pg_port}/{self.pg_db}?sslmode={self.ssl_mode}"
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.gpt3_5_turbo_0125_llm = ChatOpenAI(
            model="gpt-3.5-turbo-0125",
            temperature=0.0,
            verbose=True
        )

    def _get_format_instruction(self) -> tuple[StructuredOutputParser, str]:
        output_parser = StructuredOutputParser.from_response_schemas(
            response_schemas=response_schemas
        )
        format_instruction = output_parser.get_format_instructions()
        return output_parser, format_instruction

    def _text_loader(self, file_path: str) -> list:
        loader = TextLoader(
            file_path=file_path,
            encoding="utf-8"
        )
        documents = loader.load()
        return documents

    def _pg_vector(self, collection_name: str) -> PGVector:
        return PGVector(
            embedding_function=self.embeddings,
            collection_name=collection_name,
            connection_string=self.connection_string
        )

    def _get_text_chunks_langchain(text: str) -> List[Document]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )
        documents = [
            Document(
                page_content=text,
                metadata={
                    'source': 'database.listings'
                }
            )
            for text in text_splitter.split_text(text)
        ]
        return documents

    def message_history(self, session_id: str):
        history = RedisChatMessageHistory(
            session_id=session_id,
            url=self.redis_database_url
        )
        return history

    def assistant(self, query: str):
        store = self._pg_vector(collection_name="mytreehouse_vectors")
        retriever = store.as_retriever()

        get_relevant_documents = retriever.get_relevant_documents(query=query)

        if len(get_relevant_documents) == 0:
            realstate_properties = f"No available properties related to query: {query}"
        else:
            realstate_properties = [
                data.page_content for data in get_relevant_documents
            ]

        cached_cities = cache.get("open_ai:cities_context")
        cities_available = cached_cities if cached_cities else "No available cities currently in the database"

        output_parser, format_instruction = self._get_format_instruction()
        chat_propmt_template = ChatPromptTemplate.from_template(
            template=chat_prompt
        )

        message = chat_propmt_template.format_messages(
            conversation_history="Human: Any available warehouse in makati?\nAi: I found a compact warehouse space for lease in Makati that might interest you. It's suitable for small-scale operations and offers 24-hour CCTV surveillance for added security. Would you like more details about this property?\n[Compact Warehouse Space for Lease in Makati, 300sqm P100,000](https://www.myproperty.ph/compact-warehouse-space-for-lease-in-makati-300sqm-100000.html)\n- Suitable for small-scale operations\n- 24-hour CCTV surveillance\n- Easy access to public transport\nHuman:How about bulacan?\nAi:I found a high-ceiling warehouse in Bulacan that might suit your needs. It's perfect for manufacturing or storage, with office and worker facilities available. Would you like more details about this property?\n[High-Ceiling Warehouse in Bulacan for Rent, 850sqm Php 230,000](https://www.myproperty.ph/high-ceiling-warehouse-in-bulacan-for-rent-850sqm-230000.html)\n- Perfect for manufacturing or storage\n- With office and worker facilities\n- Near NLEX for easy logistics\nHuman: What was the first recommendation you gave me? and what is my first query to you?\nAi: I recommended a compact warehouse space for lease in Makati that is suitable for small-scale operations and offers 24-hour CCTV surveillance. Your first query to me was about any available warehouse in Makati.\n[Compact Warehouse Space for Lease in Makati, 300sqm Php 100,000](https://www.myproperty.ph/compact-warehouse-space-for-lease-in-makati-300sqm-100000.html)\n- Suitable for small-scale operations\n- 24-hour CCTV surveillance\n- Easy access to public transport",
            available_cities=cities_available,
            realstate_properties=realstate_properties,
            format_instructions=format_instruction,
            question=query,
        )

        response = self.gpt3_5_turbo_0125_llm.invoke(message)
        output_dict = output_parser.parse(response.content)

        return output_dict
