from langchain.output_parsers import ResponseSchema

query_classifier_realstate_schema = [
    ResponseSchema(
        name="query_type",
        description="'real_estate' (must include at least the property type), 'general_inquiry' (for general questions about services or properties), 'user_satisfaction' (to gauge user satisfaction with the service), or 'user_feedback' (for specific feedback on properties or services)"
    ),
    ResponseSchema(
        name="user_preference",
        description="enhance vector search formulation by extracting user preferences for property features, location, property type, and specific requirements."
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
        description="For the real estate query type, this schema is responsible for generating a comprehensive query that incorporates all relevant extracted information for input into our vector search engine.",
    ),
]
