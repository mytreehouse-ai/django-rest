import json
from logging import getLogger
from rest_framework.generics import UpdateAPIView
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from ..serializers.update_property_webhook_serializer import UpdatePropertyWebhookSerializer
from ..serializers.scraperapi_job_finished_response_serializer import ScraperApiWebhookJobFinishedResponseSerializer
from domain.models.city_model import CityModel


logger = getLogger(__name__)


class UpdatePropertyWebhookAPIView(UpdateAPIView):
    """
    API view to update properties via webhook.

    This view extends the UpdateAPIView to provide a method for handling PATCH requests. 
    It is designed to receive updates for properties from a webhook, deserialize the data using 
    the UpdatePropertyWebhookSerializer, and perform necessary actions based on the received data.

    Attributes:
        permission_classes (list): A list of permission classes that determines who can access this view. 
                                   It requires either an API key or user authentication.
        serializer_class (Serializer): The serializer class used for request data validation and deserialization. 
                                        Set to UpdatePropertyWebhookSerializer.
        http_method_names (list): A list of HTTP method names that this view will respond to. 
                                  This view only responds to PATCH requests.

    Methods:
        patch(request, *args, **kwargs): Handles PATCH requests. It deserializes the request data, 
                                         validates it, and processes the update as needed.
    """
    permission_classes = [HasAPIKey | IsAuthenticated]
    serializer_class = UpdatePropertyWebhookSerializer
    http_method_names = ["patch"]

    @swagger_auto_schema(
        operation_description="Updates property information based on webhook data.",
        operation_id="update_property_via_webhook",
        request_body=UpdatePropertyWebhookSerializer(),
        responses={
            200: ScraperApiWebhookJobFinishedResponseSerializer()
        },
        tags=["Scrapy-job"],
    )
    def patch(self, request, *args, **kwargs):
        """
        Handles PATCH requests to update property information based on webhook data.

        It uses the UpdatePropertyWebhookSerializer to deserialize and validate the request data. 
        After validation, it processes the update as needed.

        Args:
            request (Request): The request object containing the update data.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A DRF Response object with a message indicating the result of the operation.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        listing_url = serializer.validated_data.get("listing_url")
        json_fields = serializer.validated_data.get("json_fields")

        print(listing_url)
        print(f"title: {json_fields.get('title', None)}")
        print(json.dumps(json_fields.get("attributes", {}), indent=4))
        print(json.dumps(json_fields.get("description", {}), indent=4))
        print(json.dumps(json_fields.get("location", {}), indent=4))

        attributes = json_fields.get("attributes", None)

        if attributes:
            if attributes.get("listing_city_id", None) and attributes.get("listing_city", None):
                city = CityModel.objects.get_or_create(
                    id=int(attributes.get("listing_city_id")),
                    name=attributes.get("listing_city")
                )

                print(city)

        return Response(
            {
                "message": "Webhook response successfully processed."
            }
        )
