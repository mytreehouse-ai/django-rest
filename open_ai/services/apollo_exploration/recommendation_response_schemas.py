from langchain.output_parsers import ResponseSchema

recommendation_response_schemas = [
    ResponseSchema(
        name="ai_suggestion",
        description="A detailed suggestion based on the user's real estate query, using only existing properties from the provided dataset. Do not fabricate property details or suggest non-existent properties."
    ),
]
