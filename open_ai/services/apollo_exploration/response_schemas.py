from langchain.output_parsers import ResponseSchema

response_schemas = [
    ResponseSchema(
        name="ai_suggestion",
        description="Include your answer here."
    ),
    ResponseSchema(
        name="property_suggestion",
        description="This is where you can enter your property recommendation. Leave it blank if you can't find any property related to the user's query."
    )
]
