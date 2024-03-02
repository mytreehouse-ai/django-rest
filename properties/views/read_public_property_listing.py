from logging import getLogger
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema

from ..serializers.read_property_listing_serializer import ReadPropertyListingSerializer
from ..services.public_property_service import PublicPropertyService

logger = getLogger(__name__)


class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom pagination class to set a default page size.
    """
    page_size = 50  # Set the default number of items per page
    # Allow client to override the page size using this query parameter
    page_size_query_param = 'page_size'
    max_page_size = 100  # Maximum limit of items per page


class ReadPublicPropertyListingAPIView(ListAPIView):
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
    search_fields = [
        "listing_title",
        "listing_url",
        "estate__building_name",
        "estate__subdivision_name",
        "estate__address",
        "estate__description"
    ]
    ordering_fields = [
        'id',
        'created_at',
        'updated_at'
    ]
    serializer_class = ReadPropertyListingSerializer
    pagination_class = CustomPageNumberPagination
    queryset = PublicPropertyService.get_all_property_listing()

    @swagger_auto_schema(
        operation_description="Retrieve a list of public property listings with support for filtering, searching, and ordering.",
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
