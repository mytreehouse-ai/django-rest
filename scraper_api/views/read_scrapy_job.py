from logging import getLogger
from rest_framework.generics import ListAPIView
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema

from ..services.scraperapi_service import ScrapyJobService
from ..serializers.read_scrapy_job_serializer import ReadScrapyJobSerializer

logger = getLogger(__name__)


class ReadScrapyJobAPIView(ListAPIView):
    permission_classes = [HasAPIKey | IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    search_fields = ["domain", "status", "attempts"]
    serializer_class = ReadScrapyJobSerializer
    pagination_class = PageNumberPagination
