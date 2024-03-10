from langchain.output_parsers import ResponseSchema

from .guidelines import price_formatting_instructions, handling_off_topic_queries, encouraging_specificity, leveraging_conversation_history

response_schemas = [
    ResponseSchema(
        name="ai_suggestion",
        description=f"""
        For property suggestions, the response should include key features such as indoor and outdoor features, always come up with follow-up questions to engage the user.
        
        For location-related queries, provide a concise list of available cities or places, and instructions for refining the search.
        
        If unclear, ask for more details. If outside AI's scope, suggest alternative resources. If no properties match, suggest ways to refine the search.
                
        Throughout the conversation, maintain a friendly tone, use conversation history for personalization, and apply formatting for clarity.
        
        {price_formatting_instructions}
        {handling_off_topic_queries}
        {encouraging_specificity}
        {leveraging_conversation_history}        
    """
    ),
    ResponseSchema(
        name="listing_url",
        description="A direct URL to the detailed page of the recommended property listing."
    ),
    ResponseSchema(
        name="listing_city",
        description="""
        The city where the recommended property is located. This information helps users filter listings based on their preferred geographical area. 
        """
    ),
    ResponseSchema(
        name="listing_type",
        description="""
        Specifies whether the recommended property is available for rent or sale, catering to different user requirements. 
        """
    ),
    ResponseSchema(
        name="listing_price",
        description=f"""
            The price of the recommended property listing in PHP. Ensure that the price is formatted according to the guidelines:
               {price_formatting_instructions}
        """
    ),
    ResponseSchema(
        name="listing_markdown_formatted",
        description="""
            Presents all the essential details of the recommended property listing. 
            The response should be structured and easily readable, including:
                - Property title
                - Key features and amenities
                - Location details
                - Price and payment terms
                - Contact information or next steps
        """
    )
]
