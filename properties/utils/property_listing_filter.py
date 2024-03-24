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
    property_type = django_filters.CharFilter(
        field_name='property_type__description',
        lookup_expr='exact'
    )
    listing_type = django_filters.NumberFilter(
        field_name='listing_type__id',
        lookup_expr='exact'
    )
    property_status = django_filters.NumberFilter(
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
    # Example usage in API: ?num_bedrooms_min=2&num_bedrooms_max=5&num_bathrooms_min=1&num_bathrooms_max=3&num_carspaces_min=1&num_carspaces_max=2
    num_bedrooms_min = django_filters.NumberFilter(
        field_name='estate__num_bedrooms',
        lookup_expr='gte'
    )
    num_bedrooms_max = django_filters.NumberFilter(
        field_name='estate__num_bedrooms',
        lookup_expr='lte'
    )
    num_bathrooms_min = django_filters.NumberFilter(
        field_name='estate__num_bathrooms',
        lookup_expr='gte'
    )
    num_bathrooms_max = django_filters.NumberFilter(
        field_name='estate__num_bathrooms',
        lookup_expr='lte'
    )
    num_carspaces_min = django_filters.NumberFilter(
        field_name='estate__num_carspaces',
        lookup_expr='gte'
    )
    num_carspaces_max = django_filters.NumberFilter(
        field_name='estate__num_carspaces',
        lookup_expr='lte'
    )
    # Example usage in API: ?indoor_features=gym&outdoor_features=pool&other_features=elevator
    indoor_features = django_filters.CharFilter(
        field_name='estate__indoor_features',
        lookup_expr='icontains'
    )
    outdoor_features = django_filters.CharFilter(
        field_name='estate__outdoor_features',
        lookup_expr='icontains'
    )
    other_features = django_filters.CharFilter(
        field_name='estate__other_features',
        lookup_expr='icontains'
    )
    # Example usage in API: ?city_id=1
    city = django_filters.NumberFilter(
        field_name='estate__city__id',
        lookup_expr='exact'
    )
