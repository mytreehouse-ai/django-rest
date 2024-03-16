from langchain.output_parsers import ResponseSchema

query_classifier_realstate_schema = [
    ResponseSchema(
        name="query_type",
        description="'This is where you will input the query classification."
    ),
    ResponseSchema(
        name="user_preference",
        description="extract user preferences for property type, including Condominium, House and Lot, Apartment, Land, and Warehouse, as well as size, features, location, and specific requirements to enhance vector search."
    ),
    ResponseSchema(
        name="for_vector_search",
        description="For the real estate query type, this schema is responsible for generating a comprehensive query that incorporates all relevant extracted information for input into our vector search engine.",
    ),
]
