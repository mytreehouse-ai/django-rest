from logging import getLogger
from django.http import Http404
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg.utils import swagger_auto_schema

from ..serializers.read_property_listing_serializer import ReadPropertyListingSerializer
from ..services.public_property_service import PublicPropertyService


logger = getLogger(__name__)


class ReadOnePublicPropertyListingAPIView(RetrieveAPIView):
    """
    API view for reading a single public property listing.

    This view allows for retrieving the details of a single public property listing identified by its URL.
    It extends the RetrieveAPIView to provide a method for retrieving a specific object.

    Attributes:
        permission_classes (list): Permissions required to access this view. Allows any user to access.
        serializer_class (Serializer): The serializer class used for the property listing instances.
    """

    permission_classes = [AllowAny]
    serializer_class = ReadPropertyListingSerializer

    def get_object(self):
        """
        Retrieves a single property listing based on the listing URL provided in the request.

        Overrides the default method to retrieve the object. If the property listing does not exist,
        it returns a 404 response.

        Returns:
            PropertyListingModel: The property listing instance if found.
            Response: A DRF Response object with a 404 status if the property listing is not found.
        """
        listing_title = self.kwargs.get('listing_title')
        property_listing = PublicPropertyService.get_one_property_listing(
            listing_title=listing_title
        )
        if property_listing is None:
            raise Http404()
        return property_listing

    @swagger_auto_schema(
        operation_description="Retrieve a single public property listing by its URL.",
        operation_id="get_public_property_listing",
        tags=["Properties"]
    )
    @method_decorator(cache_page(60 * 15))
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve a single public property listing.

        This method is decorated to cache the response for 15 minutes to optimize performance.

        Args:
            request (Request): The request object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A DRF Response object containing the property listing data.
        """
        return super().get(request, *args, **kwargs)
