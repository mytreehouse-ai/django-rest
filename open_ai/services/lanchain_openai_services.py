import os
import logging
from typing import List
from pymongo import MongoClient
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_openai import ChatOpenAI, OpenAIEmbeddings


logger = logging.getLogger(__name__)

class MongoDBConnector:
    """
    A MongoDB Connector class for reusing the MongoDB connection.
    """
    def __init__(self, uri):
        """
        Initialize the MongoDB connection.

        :param uri: MongoDB connection URI string.
        """
        self.client = MongoClient(uri)
        self.db = self.client.mytreehouse
        self.vectors_collection = self.db.warehouses

    def insert_vector_data(self, original_data, vector_data):
        """
        Inserts a single vector data into the MongoDB collection.

        :param original_data: The original data associated with the vector.
        :param vector_data: The vector data to be inserted.
        """
        self.vectors_collection.insert_one({"original_data": original_data, "vector_data": vector_data})

    def search_vectors(self, query_vector, num_results=10):
        """
        Searches the MongoDB collection for the vectors closest to the query vector
        and returns only the original data.

        :param query_vector: The query vector to search for.
        :param num_results: The number of closest vectors to return.
        :return: A list of the original data from the closest vectors found in the collection.
        """

        # Ensure the query_vector is in the correct format (array) before searching
        if not isinstance(query_vector, list):
            raise ValueError("query_vector must be a list of floats")

        search_results = self.vectors_collection.aggregate([
            {
                "$vectorSearch": {
                    "queryVector": query_vector,
                    "path": "vector_data",
                    "numCandidates": num_results * 20,
                    "limit": num_results,
                    "index": "VectorSearchIndex"
                }
            },
            {
                "$sort": {
                    "score": -1 
                }
            },
            {
                "$project": {
                    "original_data": 1,
                    "score": 1,
                    "_id": 0
                }
            }
        ])

        return [result['original_data'] for result in search_results]

    def close(self):
        """
        Closes the MongoDB connection.
        """
        self.client.close()

class LangchainOpenAIServices:
    """
    Provides local services for OpenAI operations such as converting text to vectors,
    storing vectors, generating prompt templates, and running chains of operations.
    """
    def __init__(self, api_key, stream=False):
        """
        Initializes the OpenAILocalServices with the given API key and streaming option.

        :param api_key: The API key for OpenAI services.
        :param stream: A boolean indicating whether to enable streaming responses.
        """
        self.llm = ChatOpenAI(
            api_key=api_key,
            model="gpt-3.5-turbo-1106",
            streaming=stream, 
            callbacks=[StreamingStdOutCallbackHandler()] if stream else [], 
            temperature=0.0  # Setting temperature to 0 for deterministic, consistent QA responses
        )

    def convert_to_vector(self, text: str):
        """
        Converts a given text to a vector using OpenAIEmbeddings.

        :param text: The text to be converted.
        :return: A vector representation of the text.
        """
        embeddings = OpenAIEmbeddings()
        return embeddings.embed_query(text)

    def vector_store(self, data: List[List[float]]) -> None:
        """
        Stores a list of vectors in the database.

        :param data: A list of vectors to be stored.
        """
        vectorstore = FAISS.from_texts(
          data, embedding=OpenAIEmbeddings()
        )
        return vectorstore.as_retriever()
    
    def prompt_template(self):
        """
        Generates a prompt template for property inquiries with specific guidelines.

        :return: A ChatPromptTemplate instance created from the predefined template.
        """
        template = """
          Answer the question based only on the following question: {context}

          Question: {question}

          When responding to a prompt unrelated to warehouse properties, always reply as a friendly assistant. Then, follow up with a prompt offering assistance with warehouse-related inquiries. 

          When responding to property inquiries, please adhere to the following guidelines:

          1. Attachment Information: Exclude any attachment details mentioned in the property description from your response.
          2. Alternative Options: If the data provides additional options, proactively recommend these to the user.
          3. Description Conciseness: Ensure property descriptions are concise yet comprehensive. Focus on key details to provide a clear overview.
          4. Warehouse Listings: If asked for a list of warehouses, limit your response to 3-5 examples. Prompt the user to specify their interest in a particular warehouse for more detailed information.
          5. For queries unrelated to warehouse, always treat them as FAQs and provide unlimited responses for industrial FAQs and always respond with complete details.
          6. Price Formatting:
              - Always present prices in PHP (Philippine Peso).
              - Omit decimal points when the price ends in .0 or .00.
          7. User Guidance for Specificity: When providing property information, advise the owner on how they can refine their query for more targeted results. Encourage specificity in their requests.
          8. If a keyword is highly similar to the description, include it in the recommendation.
          9. If the user doesn't mention the warehouse, please assume they are looking for one.
          10. It is important to be specific about the location. If the user asks for Makati, only provide the Makati warehouse location, and if they ask for Taguig, provide the Taguig location, and so on.
          10. Markdown Format: All responses should be formatted in markdown for clarity and readability.

          Follow this response format for warehouse inquiry:

          -- Insert here your explanation of why you recommend the properties.

          Listing Title:
          Listing URL:
          Listing type:
          Current Price:
          Lot Area:
          Address:
          Longitude:
          Latitude:
          description:

          -- Include any additional suggestions, questions, or clarifications that will help improve your results.

          This is an example of a single response a user wants:

          ---example start---
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

          Note: The first warehouse is 515 sqm and the second one is 327 sqm. If you have a more specific requirement regarding the size, please let us know.

          If you have any further questions or need more details about these warehouses, please let me know.
          ---example end---
          """
        return ChatPromptTemplate.from_template(template)
    
    def run_chain(self, question: str, num_results=50):
        """
        Executes a chain of operations to process a question and return relevant results.

        :param question: The question to be processed.
        :param num_results: The number of results to return.
        :return: The result of invoking the chain of operations with the question.
        """
        mongodb_uri = os.environ.get('MONGODB_URI', None)
        mongodb = MongoDBConnector(mongodb_uri)
        vector_question = self.convert_to_vector(text=question)
        warehouse_data = mongodb.search_vectors(query_vector=vector_question, num_results=num_results)            

        chain = (
            {"context": self.vector_store(data=warehouse_data), "question": RunnablePassthrough()}
            | self.prompt_template()
            | self.llm
            | StrOutputParser()
        )

        return chain.invoke(question)