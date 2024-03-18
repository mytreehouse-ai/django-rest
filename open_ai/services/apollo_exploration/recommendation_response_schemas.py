from langchain.output_parsers import ResponseSchema

recommendation_response_schemas = [
    ResponseSchema(
        name="ai_suggestion",
        description="Include your answer here. Please note, it is crucial that all recommendations are presented in a well-structured markdown format"
    ),
]
