import os
from typing import List, Optional
from logging import getLogger
from openai import OpenAI, BadRequestError, RateLimitError, APIError
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
        self._pg_host = os.getenv("POSTGRES_HOST")
        self._pg_user = os.getenv("POSTGRES_USERNAME")
        self._pg_pass = os.getenv("POSTGRES_PASSWORD")
        self._pg_db = os.getenv("POSTGRES_DATABASE")
        self._pg_port = os.getenv("POSTGRES_PORT")
        self._ssl_mode = "require" if os.getenv(
            "POSTGRES_SSL_ON") == "1" else "disable"
        self._redis_database_url = os.getenv("REDIS_CACHE_URL")
        self._connection_string = f"postgresql+psycopg2://{self._pg_user}:{self._pg_pass}@{self._pg_host}:{self._pg_port}/{self._pg_db}?sslmode={self._ssl_mode}"
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.gpt3_5_turbo_0125_llm = ChatOpenAI(
            model="gpt-3.5-turbo-0125",
            temperature=0.0
        )
        self.gpt4_turbo_preview_llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.0
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

    def get_text_chunks_langchain(self, text: str) -> List[Document]:
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

    def pg_vector(self, collection_name: str) -> PGVector:
        return PGVector(
            embedding_function=self.embeddings,
            collection_name=collection_name,
            connection_string=self._connection_string
        )

    def get_message_history(self, thread_id: str):
        history = RedisChatMessageHistory(
            session_id=thread_id,
            url=self._redis_database_url
        )
        return history

    def assistant(self, query: str, collection_name: str, thread_id: Optional[str] = None):
        store = self.pg_vector(collection_name=collection_name)
        retriever = store.as_retriever()

        conversation_history = "This is a new query no conversation history at the moment"
        available_properties = """"""

        if thread_id:
            get_conversation_history = self.get_message_history(
                thread_id=thread_id
            )

            if len(get_conversation_history.messages) > 0:
                conversation_history = """"""
                for message in get_conversation_history.messages:
                    message_json = message.to_json()
                    message_data = message_json.get("kwargs")
                    message_type = message_data.get('type')
                    message_content = message_data.get('content')
                    conversation_history += f"{message_type.title()}: {message_content}\n"

        get_relevant_documents = retriever.get_relevant_documents(query=query)
        if len(get_relevant_documents) == 0:
            realstate_properties = f"No available properties related to query: {query}"
        else:
            realstate_properties = [
                data.page_content for data in get_relevant_documents
            ]
            if isinstance(realstate_properties, str):
                available_properties = realstate_properties
            else:
                for property_data in realstate_properties:
                    available_properties += property_data + "\n"

        cached_cities = cache.get("open_ai:cities_context")
        cities_available = cached_cities if cached_cities else "No available cities currently in the database"

        output_parser, format_instruction = self._get_format_instruction()
        chat_propmt_template = ChatPromptTemplate.from_template(
            template=chat_prompt
        )

        message = chat_propmt_template.format_messages(
            conversation_history=conversation_history,
            available_cities=cities_available,
            realstate_properties=available_properties,
            format_instructions=format_instruction,
            question=query,
        )

        try:
            response = self.gpt3_5_turbo_0125_llm.invoke(message)
            output_dict = output_parser.parse(response.content)
            if get_conversation_history:
                get_conversation_history.add_user_message(message=query)
                get_conversation_history.add_ai_message(
                    message=f"{output_dict.get('ai_suggestion')}\n{output_dict.get('listing_markdown_formatted')}"
                )
        except BadRequestError as e:
            output_dict = {
                "detail": f"BadRequestError: {str(e)}",
                "status_code": 400
            }
            print(f"BadRequestError: {str(e)}")
        except RateLimitError as e:
            output_dict = {
                "detail": f"RateLimitError: {str(e)}",
                "status_code": 429
            }
            print(f"RateLimitError: {str(e)}")
        except APIError as e:
            output_dict = {
                "detail": f"APIError: {str(e)}",
                "status_code": 500
            }
            print(f"APIError: {str(e)}")

        return output_dict
