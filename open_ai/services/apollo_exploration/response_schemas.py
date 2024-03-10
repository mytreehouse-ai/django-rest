from langchain.output_parsers import ResponseSchema

ai_suggestion_schema = ResponseSchema(
    name="ai_suggestion",
    description="""
    For property suggestions, the response should include:
        - A brief overview of the suggested property and its key features
        - Reasons for the recommendation based on the user's query and preferences
        - Pros and cons of the property (if applicable)
        - Any additional insights or advice related to the suggestion
        - Follow-up questions to the user to promote a more engaging and personalized property
    search experience, such as:
        - Seeking clarification on the user's preferences or requirements
        - Suggesting additional filters or criteria to refine the search
        - Offering alternative options or recommendations based on the user's input
        - Encouraging the user to provide more details for a more accurate property match
    For location-related queries (e.g., available cities or places), the response should include:
        - A clear and concise list of the available cities or places in the database
        - Instructions on how the user can utilize this information to refine their property search
        - Encouragement for the user to provide more specific criteria for a more targeted search
        - An offer to assist the user further with any other questions or requirements
        - Follow-up questions to the user to gather more information about their preferred location, such as:
            - Asking if any of the listed locations match their preferences
            - Inquiring if they have a specific place or neighborhood in mind
            - Encouraging them to provide more details about their ideal location
    If no suitable properties are found or if the database does not contain any locations matching the user's query, the response should:
        - Inform the user that no matching results were found
        - Suggest alternative locations or property types that the user might consider
        - Provide guidance on how the user can modify their search criteria for better results
        - Assure the user that the AI is ready to help with any further inquiries or requirements
        - Ask follow-up questions to better understand the user's needs and preferences, such as:
            - Inquiring about their budget range or desired amenities
            - Suggesting related locations or property types that might interest them
            - Encouraging them to provide more context about their search criteria
            
        Additionally, include a friendly and informative message when no suitable listings are found:
            - Acknowledge that no properties matching the user's query were found within the given context
            - Suggest alternative search criteria or related property types that the user might explore
            - Encourage the user to modify their query or preferences for better results
            - Provide guidance on how to refine the search for more relevant listings
            - Assure the user that the AI is ready to assist with any further inquiries
    """
)

listing_url_schema = ResponseSchema(
    name="listing_url",
    description="A direct URL to the detailed page of the recommended property listing. If no suitable property is found, leave this field blank."
)

listing_city_schema = ResponseSchema(
    name="listing_city",
    description="""
    The city where the recommended property is located. This information helps users filter listings based on their preferred geographical area. 
    If no suitable property is found, leave this field blank.
    """
)

listing_type_schema = ResponseSchema(
    name="listing_type",
    description="""
    Specifies whether the recommended property is available for rent or sale, catering to different user requirements. 
    If no suitable property is found, leave this field blank.
    """
)

listing_price_schema = ResponseSchema(
    name="listing_price",
    description="""
        The price of the recommended property listing in PHP. Ensure that the price is formatted according to the guidelines:
            - Omit decimal points when the price ends in .0 or .00
            - Use commas as thousands separators (e.g., Php 1,500,000)
        If no suitable property is found, leave this field blank.
    """
)

listing_markdown_formatted_schema = ResponseSchema(
    name="listing_markdown_formatted",
    description="""
        A markdown-formatted response that presents all the essential details of the recommended property listing. 
        The response should be structured and easily readable, including:
            - Property title
            - Key features and amenities
            - Location details
            - Price and payment terms
            - Contact information or next steps
        If no suitable property is found, leave this field blank.
    """
)

response_schemas = [
    ai_suggestion_schema,
    listing_url_schema,
    listing_city_schema,
    listing_type_schema,
    listing_price_schema,
    listing_markdown_formatted_schema,
]
