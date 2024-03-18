from langchain.output_parsers import ResponseSchema

query_classifier_realstate_schema = [
    ResponseSchema(
        name="query_type",
        description="'This is where you will input the query classification."
    ),
    ResponseSchema(
        name="user_preference",
        description="Extract user preferences for property type, including Condominium, House and Lot, Apartment, Land, and Warehouse. Also, gather information on size, features, location, and specific requirements to enhance vector search. Be sure to update preferences if they change."
    ),
    ResponseSchema(
        name="for_vector_search",
        description="For the real estate query type, this schema is responsible for generating a comprehensive query that incorporates all relevant extracted information for input into our vector search engine. Keep this a string format example: 'property_type: condominium budget_price: 10,000,000.00 - 20,000,000.00 location: taguig features: with swimming pool etc... include important information to improve the similarity search.'",
        type="string"
    ),
]
