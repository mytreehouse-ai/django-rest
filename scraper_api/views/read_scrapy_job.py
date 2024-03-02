from logging import getLogger
from rest_framework.generics import ListAPIView
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema

from ..utils.scrapy_job_filter import ScrapyJobFilters
from ..services.scraperapi_service import ScrapyJobService
from ..serializers.read_scrapy_job_serializer import ReadScrapyJobSerializer

logger = getLogger(__name__)


class ReadScrapyJobAPIView(ListAPIView):
    """
    API view to retrieve a paginated list of Scrapy jobs.

    This view extends the ListAPIView to provide a method for retrieving a list of Scrapy jobs
    that have been initiated or completed. It supports filtering by domain, status, and attempts,
    and allows for ordering and pagination of the results.

    Attributes:
        permission_classes (list): Permissions required to access this view. Supports API key or user authentication.
        filter_backends (list): Defines the filtering backends used for this view.
        search_fields (list): Fields of the ScrapyJobModel that can be searched.
        serializer_class (Serializer): The serializer class used for Scrapy job instances.
        pagination_class (Type[PageNumberPagination]): The pagination class used to paginate the results.
        queryset (QuerySet): The initial queryset that lists all Scrapy jobs for Selenium processing.
    """
    permission_classes = [HasAPIKey | IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    filterset_class = ScrapyJobFilters
    search_fields = [
        "job_id",
        "domain",
        "status",
        "status_url",
        "attempts"
    ]
    ordering_fields = [
        'id',
        'attempts',
        'created_at'
    ]
    serializer_class = ReadScrapyJobSerializer
    pagination_class = PageNumberPagination
    queryset = ScrapyJobService.get_all_scrapy_job_for_selenium()

    @swagger_auto_schema(
        operation_description="Retrieve a paginated list of Scrapy jobs.",
        operation_id="scrapy_job_paginated_list",
        tags=["Scrapy-job"],
    )
    def get(self, request, *args, **kwargs):
        """
        Retrieves a paginated list of Scrapy jobs based on the provided query parameters.

        Args:
            request (Request): The request object containing query parameters for filtering and pagination.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A DRF Response object containing the paginated list of Scrapy jobs.
        """
        return super().get(request, *args, **kwargs)
