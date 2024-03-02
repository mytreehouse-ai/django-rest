import logging
from django_filters import rest_framework as filters
from django_filters import BaseInFilter, NumberFilter, DateFromToRangeFilter

logger = logging.getLogger(__name__)


class ScrapyJobFilters(filters.FilterSet):
    # Filter for reference number using exact match
    job_id = filters.CharFilter(
        lookup_expr='exact'
    )
    # Filter for single_page using exact match
    single_page = filters.BooleanFilter(
        lookup_expr='exact'
    )
    # Filter for status using exact match
    status = filters.CharFilter(
        lookup_expr='exact'
    )
    # Filter for is_processed using exact match
    is_multi_page_processed = filters.BooleanFilter(
        lookup_expr='exact'
    )
    is_single_page_processed = filters.BooleanFilter(
        lookup_expr='exact'
    )
