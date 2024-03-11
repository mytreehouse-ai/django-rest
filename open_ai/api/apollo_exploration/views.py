import os
from logging import getLogger
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from .serializer import ApolloExplorationAiQueryParamsSerializer, ReadApolloExplorationAiResponseSerializer
from open_ai.services.apollo_exploration.service import ApolloExplorationService

logger = getLogger(__name__)


class ApolloExplorationAiAPIView(RetrieveAPIView):
    """
    API view for handling requests to the Apollo Exploration AI.

    This view allows clients to retrieve AI-generated responses based on a given query, collection name, and an optional thread ID.

    Attributes:
        permission_classes (list): Specifies that any user can access this view without authentication.
        serializer_class (Serializer): The serializer class used for validating query parameters.
    """

    permission_classes = [AllowAny]
    serializer_class = ReadApolloExplorationAiResponseSerializer

    def get_object(self):
        """
        Retrieves an object based on the validated query parameters.

        This method extracts query parameters, validates them using the ApolloExplorationAiQueryParamsSerializer,
        and then uses these parameters to request a response from the Apollo Exploration Service.

        Returns:
            dict: The response from the Apollo Exploration Service.
        """
        query_params = self.request.query_params
        serialize_query_params = ApolloExplorationAiQueryParamsSerializer(
            data=query_params
        )
        serialize_query_params.is_valid(raise_exception=True)

        query = serialize_query_params.validated_data.get("query")
        collection_name = serialize_query_params.validated_data.get(
            "collection_name")
        thread_id = serialize_query_params.validated_data.get(
            "thread_id", None)

        apollo_exporation_service = ApolloExplorationService(
            api_key=os.getenv("OPENAI_API_KEY"))

        return apollo_exporation_service.assistant(collection_name=collection_name, query=query, thread_id=thread_id)

    @swagger_auto_schema(
        operation_description="Retrieve AI-generated responses for a given query.",
        operation_id="get_apollo_exploration_response",
        query_serializer=ApolloExplorationAiQueryParamsSerializer(),
        responses={200: ReadApolloExplorationAiResponseSerializer()},
        tags=["Apollo Exploration"]
    )
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve AI-generated responses.

        This method overrides the default get method to provide custom functionality for retrieving AI-generated responses
        based on the provided query parameters.

        Args:
            request (Request): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: The response object containing the AI-generated response or an error message.
        """
        return super().get(request, *args, **kwargs)
