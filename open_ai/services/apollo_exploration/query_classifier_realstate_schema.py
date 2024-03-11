from langchain.output_parsers import ResponseSchema

query_classifier_realstate_schema = [
    ResponseSchema(
        name="query_type",
        description="'real_estate' or 'non_real_estate'"
    ),
    ResponseSchema(
        name="location",
        description="extracted location or n/a"
    ),
    ResponseSchema(
        name="property_type",
        description="extracted property or n/a"
    ),
    ResponseSchema(
        name="budget_min",
        description="extracted maximum budget or 0.",
        type="float"
    ),
    ResponseSchema(
        name="budget_max",
        description="extracted maximum budget. Set 0 if none.",
        type="float"
    ),
    ResponseSchema(
        name="budget_min_formatted",
        description="extracted maximum budget in Php format or 0",
        type="float"
    ),
    ResponseSchema(
        name="budget_max_formatted",
        description="extracted maximum budget in Php format. Set 0 if none.",
    ),
    ResponseSchema(
        name="features",
        description="['extracted feature 1', 'extracted feature 2', '...'] or []",
        type="list[string]"
    ),
    ResponseSchema(
        name="for_vector_search",
        description="For the real estate query type, please generate a query based on the extracted information that we can input into our vector search. If there is a valid property type, please include it in the query (e.g. property_type: condominium). You can include this even if there is no other information to add, or leave it empty if query type is none real estate related.",
    ),
]
