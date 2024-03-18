from logging import getLogger
from rest_framework import serializers


logger = getLogger(__name__)


class ReadApolloExplorationAiResponseSerializer(serializers.Serializer):
    """
    Serializer for reading AI response in Apollo Exploration.

    Attributes:
        ai_suggestion (CharField): The AI-generated suggestion or response.
    """
    ai_suggestion = serializers.CharField()

    class Meta:
        """
        Meta class to define serializer behavior.
        """
        ref_name = "ApolloExplorationAi.read"


class ApolloExplorationAiQueryParamsSerializer(serializers.Serializer):
    """
    Serializer for query parameters sent to Apollo Exploration AI.

    Attributes:
        query (CharField): The query or prompt to be processed by the AI.
        collection_name (CharField): The name of the collection to be queried.
        thread_id (CharField, optional): An optional thread ID for threading queries.
    """
    query = serializers.CharField(required=True)
    collection_name = serializers.CharField(required=True)
    thread_id = serializers.CharField(required=True)
    llm = serializers.ChoiceField(
        choices=[
            ("gpt-3.5-turbo-0125", "gpt-3.5-turbo-0125"),
            ("gpt-4-0125-preview", "gpt-4-0125-preview"),
            ("mixtral-8x7b-32768", "mixtral-8x7b-32768")
        ],
        default="gpt-3.5-turbo-0125",
        required=False
    )

    class Meta:
        """
        Meta class to define serializer behavior.
        """
        ref_name = "ApolloExplorationAi.query-params"
