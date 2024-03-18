import os
import json
from typing import List, Optional
from logging import getLogger
from groq import Groq
from openai import OpenAI, BadRequestError, RateLimitError, APIError
from django.core.cache import cache
from langchain.vectorstores.pgvector import PGVector
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.output_parsers import StructuredOutputParser
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import ChatPromptTemplate
from langchain.output_parsers import ResponseSchema
from langchain.schema.document import Document

from .recommendation_response_schemas import recommendation_response_schemas
from .recommendation_prompt_template import recommendation_prompt_template
from .query_classifier_realstate_schema import query_classifier_realstate_schema
from .query_classifier_prompt_template import query_classifier_prompt_template


logger = getLogger(__name__)


class ApolloExplorationService:
    def __init__(self, api_key: str):
        OpenAI(api_key=api_key)
        self.groq_client = Groq(
            api_key=os.environ.get("GROQAI_API_KEY"),
        )
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
        self.gpt4_0125_preview_llm = ChatOpenAI(
            model="gpt-4-0125-preview",
            temperature=0.5
        )

    def get_format_instruction(self, response_schema: List[ResponseSchema]) -> tuple[StructuredOutputParser, str]:
        output_parser = StructuredOutputParser.from_response_schemas(
            response_schemas=response_schema
        )
        format_instruction = output_parser.get_format_instructions()
        return output_parser, format_instruction

    def text_loader(self, file_path: str) -> list:
        loader = TextLoader(
            file_path=file_path,
            encoding="utf-8"
        )
        documents = loader.load()
        return documents

    def get_text_chunks_langchain(self, text: str) -> List[Document]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024,  # Optimal chunk size for balanced performance and coherence
            chunk_overlap=100  # Increased overlap for better context retention between chunks
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

    def query_classifier(self, query: str, thread_id: str):
        user_preference_log_history = self.get_message_history(
            thread_id=f"{thread_id}:user_preference_log"
        )

        memory = ConversationBufferMemory(
            memory_key="user_preference_log", chat_memory=user_preference_log_history
        )

        output_parser, format_instruction = self.get_format_instruction(
            response_schema=query_classifier_realstate_schema
        )
        chat_query_classifier_prompt_template = ChatPromptTemplate.from_template(
            template=query_classifier_prompt_template
        )
        message = chat_query_classifier_prompt_template.format_messages(
            query=query,
            user_preference_log=memory.chat_memory,
            format_instruction=format_instruction
        )

        ai_classifier_response = self.gpt4_0125_preview_llm.invoke(
            input=message
        )

        query_classifer = output_parser.parse(ai_classifier_response.content)

        query_type = query_classifer.get("query_type", "")
        user_preference = query_classifer.get("user_preference", "")

        if user_preference and query_type == "real_estate":
            user_preference_log_history.add_user_message(
                message=user_preference
            )

        user_preference_log = memory.chat_memory

        return query_classifer, user_preference_log

    def assistant(self, query: str, collection_name: str, thread_id: str, llm: Optional[str] = "gpt-3.5-turbo-0125"):
        available_properties = """"""

        query_classifer, user_preference_log = self.query_classifier(
            query=query,
            thread_id=thread_id
        )

        print(json.dumps(query_classifer, indent=4))

        get_conversation_history = self.get_message_history(
            thread_id=f"{thread_id}:user_conversation_history"
        )

        query_type = query_classifer.get("query_type", "")
        user_preference = query_classifer.get("user_preference", "")

        if query_type == "real_estate":
            store = self.pg_vector(collection_name=collection_name)

            get_relevant_documents = store.similarity_search_with_score(
                query=query_classifer.get("for_vector_search"),
                k=12,
            )

            if len(get_relevant_documents) == 0:
                available_properties = f"No available properties related to query: {query}"
            else:
                for relevant_doc in get_relevant_documents:
                    data, _similarity_score = relevant_doc
                    available_properties += data.page_content + "\n"

        cached_cities = cache.get("open_ai:cities_context")
        cities_available = cached_cities if cached_cities else "No available cities currently in the database"

        output_parser, format_instruction = self.get_format_instruction(
            response_schema=recommendation_response_schemas
        )
        chat_recommendation_prompt_template = ChatPromptTemplate.from_template(
            template=recommendation_prompt_template
        )

        memory = ConversationBufferMemory(
            memory_key="conversation_history", chat_memory=get_conversation_history
        )

        message = chat_recommendation_prompt_template.format_messages(
            question=query,
            user_preference_log=user_preference_log,
            available_properties=available_properties,
            conversation_history=memory.chat_memory,
            format_instructions=format_instruction,
        )

        try:
            if llm == "gpt-4-0125-preview":
                # response = self.gpt4_0125_preview_llm.invoke(message)
                response = self.groq_client.chat.completions.create(
                    messages=message,
                    model="mixtral-8x7b-32768",
                )
            else:
                response = self.gpt3_5_turbo_0125_llm.invoke(message)

            output_dict = output_parser.parse(response.content)
            get_conversation_history.add_user_message(message=query)
            get_conversation_history.add_ai_message(
                message=f"{output_dict.get('ai_suggestion')}"
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
