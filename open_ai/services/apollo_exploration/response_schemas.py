from langchain.output_parsers import ResponseSchema

response_schemas = [
    ResponseSchema(
        name="ai_suggestion",
        description="Include your answer here."
    ),
    ResponseSchema(
        name="property_suggestion",
        description="""
       A markdown-formatted response:
       
        - [Listing title](Listing URL)
        - Price
        - Listing type
        - Property type
        - Lot area or Building size
        - Floor area if available
        - Address if available
        - City
        - Building name or subdivision name
        - Bedrooms if available
        - Bathrooms if available
        - Parking space if available
        - Listing description, indoor, outdoor, and other features if available
        
        Leave it blank if you can't find any property related to the user's query.
        """
    )
]
