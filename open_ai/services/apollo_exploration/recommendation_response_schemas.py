from langchain.output_parsers import ResponseSchema

recommendation_response_schemas = [
    ResponseSchema(
        name="ai_suggestion",
        description="A detailed suggestion based on the user's real estate query."
    ),
]
