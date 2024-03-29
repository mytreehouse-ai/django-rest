from langchain.output_parsers import ResponseSchema

query_classifier_realstate_schema = [
    ResponseSchema(
        name="query_type",
        description="'This is where you will input the query classification."
    ),
    ResponseSchema(
        name="user_preference",
        description="Please gather user preferences for the type of property they are interested in, including Condominiums, Houses and Lots, Apartments, Land, and Warehouses. Additionally, collect information on the size, features, location, and any specific requirements that would improve the vector search. Ensure that preferences are updated if they change and avoid repeating the same preference."
    ),
    ResponseSchema(
        name="for_vector_search",
        description="This schema plays a pivotal role in the real estate query processing by crafting a detailed query string that encapsulates all pertinent information extracted from the user's request. This query string is then utilized as input for the vector search engine to identify the most relevant property listings. The format of the query string should be comprehensive and structured, including key details such as property type, budget range, desired location, and specific features that the user is looking for. An example format could be: 'property_type: condominium; budget_price: ₱ 10,000,000.00 - ₱ 20,000,000.00 must be include the (₱); location: Taguig; features: with swimming pool, two-car garage, etc.' This structured approach ensures that the vector search can effectively match the user's preferences with suitable property listings, thereby enhancing the accuracy and relevance of the search results.",
        type="string"
    ),
]
