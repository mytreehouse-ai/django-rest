from logging import getLogger
import django_filters

logger = getLogger(__name__)


class PropertyListingFilter(django_filters.FilterSet):
    # Example usage in API: ?price_min=500000&price_max=1000000
    price_min = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='gte'
    )
    price_max = django_filters.NumberFilter(
        field_name='price',
        lookup_expr='lte'
    )
    # Example usage in API: ?property_type_id=1&listing_type_id=2&property_status_id=3
    property_type_id = django_filters.NumberFilter(
        field_name='property_type__id',
        lookup_expr='exact'
    )
    listing_type_id = django_filters.NumberFilter(
        field_name='listing_type__id',
        lookup_expr='exact'
    )
    property_status_id = django_filters.NumberFilter(
        field_name='property_status__id',
        lookup_expr='exact'
    )
    # Example usage in API: ?lot_size_min=100&lot_size_max=500&floor_size_min=50&floor_size_max=300&building_size_min=200&building_size_max=1000
    lot_size_min = django_filters.NumberFilter(
        field_name='estate__lot_size',
        lookup_expr='gte'
    )
    lot_size_max = django_filters.NumberFilter(
        field_name='estate__lot_size',
        lookup_expr='lte'
    )
    floor_size_min = django_filters.NumberFilter(
        field_name='estate__floor_size',
        lookup_expr='gte'
    )
    floor_size_max = django_filters.NumberFilter(
        field_name='estate__floor_size',
        lookup_expr='lte'
    )
    building_size_min = django_filters.NumberFilter(
        field_name='estate__building_size',
        lookup_expr='gte'
    )
    building_size_max = django_filters.NumberFilter(
        field_name='estate__building_size',
        lookup_expr='lte'
    )
