from logging import getLogger
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema

# from ..utils.city_filter import CityFilter
from ..services.domain_service import DomainService
from ..serializer.read_city_serializer import ReadCitySerializer
from domain.utils.custom_page_number_pagination import CustomPageNumberPagination

logger = getLogger(__name__)


class ReadAllCityAPIView(ListAPIView):
    """
    API view for reading all cities.

    This view allows for listing all cities with support for searching and ordering.
    It supports pagination through `CustomPageNumberPagination`.
    """
    permission_classes = [AllowAny]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    # filterset_class = CityFilter  # Uncomment and implement CityFilter for filtering capabilities.
    search_fields = [
        "name",
    ]
    ordering_fields = [
        "id",
        "name",
        "created_at",
        "updated_at"
    ]
    serializer_class = ReadCitySerializer
    pagination_class = CustomPageNumberPagination
    queryset = DomainService.get_all_city()

    @swagger_auto_schema(
        operation_description="Retrieve a list of all cities. Supports searching by city name and ordering by id, created_at, and updated_at.",
        operation_id="list_all_cities",
        tags=["Domains"],
    )
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to retrieve a list of all cities.

        Supports searching by city name and ordering by id, created_at, and updated_at.

        Args:
            request (Request): The request object containing query parameters.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A DRF Response object containing the paginated list of cities.
        """
        return super().get(request, *args, **kwargs)
