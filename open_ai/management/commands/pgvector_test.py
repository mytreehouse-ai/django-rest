import os
import json
from typing import List
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
from langchain.schema.document import Document

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

        """
            select document (embedding <=> '[-0.2372847.....]') as cosine_distance
            from langchain_pg_embedding
            order by cosine_distance
            limit 2
        """
