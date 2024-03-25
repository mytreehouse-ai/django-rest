from logging import getLogger
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg.utils import swagger_auto_schema

from ..services.domain_service import DomainService

logger = getLogger(__name__)


class ReadAllCityAPIView(ListAPIView):
    """
    API view to retrieve a list of all cities available in the database.

    This view extends the ListAPIView to leverage Django Rest Framework's capabilities for listing resources.
    It utilizes the DomainService to fetch all cities and supports additional functionalities such as searching
    and ordering by specific fields like city name, id, created_at, and updated_at through query parameters.
    """
    permission_classes = [AllowAny]
    queryset = DomainService.get_all_city()

    @swagger_auto_schema(
        operation_description="Retrieve a list of all cities. Supports searching by city name and ordering by id, created_at, and updated_at.",
        operation_id="list_all_cities",
        tags=["Domains"],
    )
    @method_decorator(cache_page(60 * 60 * 2))
    def get(self, request, *args, **kwargs):
        """
        Overridden GET method to handle the retrieval of all cities.

        This method enhances the base ListAPIView's get method by providing detailed documentation on its functionality
        and the supported query parameters for searching and ordering. It returns a paginated list of cities based on
        the provided query parameters.

        Args:
            request (Request): The request object containing query parameters for searching and ordering.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A DRF Response object containing the paginated list of cities, adhering to the specified search
            and ordering criteria.
        """
        return super().get(request, *args, **kwargs)
