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
from properties.models.listing_type_model import ListingTypeModel
from properties.models.property_type_model import PropertyTypeModel
from properties.models.property_status_model import PropertyStatusModel
from properties.models.property_listing_model import PropertyListingModel
from scraper_api.models.scrapy_job_model import ScrapyJobModel


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

        attributes = json_fields.get("attributes", None)

        try:
            property_listing = PropertyListingModel.objects.get(
                listing_url=listing_url
            )
        except PropertyListingModel.DoesNotExist:
            deleted_count, _ = ScrapyJobModel.objects.filter(
                domain=listing_url).delete()
            if deleted_count > 0:
                logger.info(
                    f"Deleted {deleted_count} ScrapyJobModel entries for domain: {listing_url}"
                )
            logger.error(
                f"No property listing found for URL: {listing_url}")
            return Response(
                {
                    "message": f"No property listing found for URL: {listing_url}"
                },
                status=404
            )

        if attributes:
            attribute_set_name = attributes.get("attribute_set_name", None)
            price_formatted = attributes.get("price_formatted", None)
            offer_type = attributes.get("offer_type", None)
            indoor_features = attributes.get("indoor_features", [])
            outdoor_features = attributes.get("outdoor_features", [])
            other_features = attributes.get("other_features", [])
            listing_address = attributes.get("listing_address", None)
            image_url = attributes.get("image_url", None)
            description = json_fields.get("description", None)
            property_type = None

            if attribute_set_name:
                try:
                    property_type = PropertyTypeModel.objects.get(
                        description=attribute_set_name
                    )
                except PropertyTypeModel.DoesNotExist:
                    if attribute_set_name == "Commercial":
                        property_type = PropertyTypeModel.objects.get(id=4)

            listing_type = None
            if offer_type == "Buy":
                listing_type = ListingTypeModel.objects.get(
                    description="For Sale"
                )
            elif offer_type == "Rent":
                listing_type = ListingTypeModel.objects.get(
                    description="For Rent"
                )

            city = None
            if attributes.get("listing_city_id", None) and attributes.get("listing_city", None):
                city, _created = CityModel.objects.get_or_create(
                    id=int(attributes.get("listing_city_id")),
                    defaults={
                        "name": attributes.get("listing_city"),
                    }
                )

            property_status_available, _property_status_created = PropertyStatusModel.objects.get_or_create(
                description="Available"
            )

            property_listing.listing_type = listing_type
            property_listing.property_type = property_type
            property_listing.price_formatted = price_formatted
            property_listing.property_status = property_status_available
            property_listing.is_active = True
            property_listing.save(
                update_fields=[
                    "listing_type",
                    "property_type",
                    "price_formatted",
                    "property_status",
                    "is_active"
                ]
            )

            if city:
                property_listing.estate.address = listing_address
                property_listing.estate.city = city
                property_listing.estate.indoor_features = indoor_features
                property_listing.estate.outdoor_features = outdoor_features
                property_listing.estate.other_features = other_features
                property_listing.estate.image_url = image_url
                property_listing.estate.description = description.get(
                    "text",
                    None
                )
                property_listing.estate.metadata = json_fields
                property_listing.estate.save(
                    update_fields=[
                        "address",
                        "city",
                        "indoor_features",
                        "outdoor_features",
                        "other_features",
                        "image_url",
                        "description",
                        "metadata"
                    ]
                )

            try:
                scrapy_job = ScrapyJobModel.objects.get(domain=listing_url)
                scrapy_job.is_single_page_processed = True
                scrapy_job.save(update_fields=["is_single_page_processed"])
                logger.info(
                    f"Scrapy job for {listing_url} marked as single page processed."
                )
            except ScrapyJobModel.DoesNotExist:
                logger.error(f"Scrapy job not found: {listing_url}")

            logger.info(
                f"Property listing found: {property_listing.listing_url}"
            )
        else:
            property_status_delisted, _property_status_created = PropertyStatusModel.objects.get_or_create(
                description="Delisted"
            )
            property_listing.property_status = property_status_delisted
            property_listing.is_active = False
            property_listing.is_delisted = True
            property_listing.save(
                update_fields=[
                    "property_status",
                    "is_active",
                    "is_delisted"
                ]
            )
            print(
                json.dumps(
                    {
                        "id": property_listing.id,
                        "listing_url": property_listing.listing_url,
                        "property_status": property_status_delisted.description,
                        "is_delisted": property_listing.is_delisted,
                    },
                    indent=4
                )
            )
            logger.info(
                f"Property listing updated to inactive and delisted: {property_listing.listing_url}"
            )

            try:
                scrapy_job = ScrapyJobModel.objects.get(domain=listing_url)
                scrapy_job.delete()
                logger.info(f"Scrapy job deleted for domain: {listing_url}")
            except ScrapyJobModel.DoesNotExist:
                scrapy_job = None
                logger.error(f"Scrapy job not found for domain: {listing_url}")

        return Response(
            {
                "message": "Webhook response successfully processed."
            }
        )
