from langchain.output_parsers import ResponseSchema

response_schemas = [
    ResponseSchema(
        name="ai_suggestion",
        description="Include your answer here."
    ),
    ResponseSchema(
        name="property_suggestion",
        description="This where you will put your property recommendation."
    )
]
