from logging import getLogger
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema

from ..serializers.read_property_listing_serializer import ReadPropertyListingSerializer
from ..services.public_property_service import PublicPropertyService
from ..utils.property_listing_filter import PropertyListingFilter
from domain.utils.custom_page_number_pagination import CustomPageNumberPagination

logger = getLogger(__name__)


class ReadAllPublicPropertyListingAPIView(ListAPIView):
    """
    API view for reading public property listings.

    This view allows for listing all public properties with support for filtering, searching, and ordering.
    It uses the `ReadPropertyListingSerializer` for serialization of property listings and supports pagination.
    """
    permission_classes = [AllowAny]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = PropertyListingFilter
    search_fields = [
        "listing_title",
        "listing_url",
        "estate__building_name",
        "estate__subdivision_name",
        "estate__address",
        "estate__description"
    ]
    ordering_fields = [
        "id",
        "created_at",
        "updated_at"
    ]
    serializer_class = ReadPropertyListingSerializer
    pagination_class = CustomPageNumberPagination
    queryset = PublicPropertyService.get_all_property_listing()

    @swagger_auto_schema(
        operation_description="""
        Retrieve a list of public property listings without requiring any authentication or authorization. This endpoint provides comprehensive support for filtering, searching, and ordering to refine search results effectively.

        **Filtering Options:**

        - `property_type_id`: Filters properties by type. Valid payloads include:
            - `1` for Condominium
            - `2` for House
            - `3` for Apartment
            - `4` for Warehouse
            - `5` for Land

        - `listing_type_id`: Filters properties by listing status. Valid payloads are:
            - `1` for For Sale
            - `2` for For Rent

        - `property_status_id`: Filters properties by their status. Valid payloads include:
            - `1` for Available
            - `2` for Under Offer
            - `3` for Sold
            - `4` Delisted property

        - `price_min` and `price_max`: Filters properties within a specific price range. For example, `?price_min=500000&price_max=1000000` filters properties priced between 500,000 and 1,000,000.

        - `lot_size_min` and `lot_size_max`: Filters properties based on the lot size in square meters. For instance, `?lot_size_min=100&lot_size_max=500` filters properties with lot sizes between 100 and 500 square meters.

        - `floor_size_min` and `floor_size_max`: Filters properties by the floor size in square meters.

        - `building_size_min` and `building_size_max`: Filters properties by the building size in square meters.

        - `num_bedrooms_min` and `num_bedrooms_max`: Filters properties by the number of bedrooms.

        - `num_bathrooms_min` and `num_bathrooms_max`: Filters properties by the number of bathrooms.

        - `num_carspaces_min` and `num_carspaces_max`: Filters properties by the number of car spaces.

        - `city_id`: Filters properties based on their city. For example, `?city_id=1` filters properties located in a specific city.

        - `indoor_features`, `outdoor_features`, and `other_features`: Filters properties by specific features. These filters support partial matches and can be combined. For example, `?indoor_features=gym&outdoor_features=pool` filters properties with gyms indoors and pools outdoors.

        These filters can be used individually or combined to tailor the search results to your specific needs, alongside the search and ordering options provided by the API.
        """,
        operation_id="list_public_property_listings",
        tags=["Properties"],
    )
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve public property listings.

        Supports filtering, searching, and ordering of property listings based on query parameters provided in the request.

        Args:
            request (Request): The request object containing query parameters.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A DRF Response object containing the paginated list of property listings.
        """
        return super().get(request, *args, **kwargs)
