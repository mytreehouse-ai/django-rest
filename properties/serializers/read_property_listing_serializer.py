from logging import getLogger
from rest_framework import serializers

from domain.serializer.read_city_serializer import ReadCitySerializer
from ..models.property_listing_model import PropertyListingModel
from ..models.property_model import PropertyModel
from ..serializers.read_property_type_serializer import ReadPropertyTypeSerializer
from ..serializers.read_listing_type_serializer import ReadListingTypeSerializer
from ..serializers.read_property_status_serializer import ReadPropertyStatusSerializer

logger = getLogger(__name__)


class ReadPropertySerializer(serializers.ModelSerializer):
    city = ReadCitySerializer(read_only=True)

    class Meta:
        ref_name = "PropertyListingModel.read"
        model = PropertyModel
        fields = [
            "id",
            "building_name",
            "subdivision_name",
            "address",
            "lot_size",
            "floor_size",
            "building_size",
            "num_bedrooms",
            "num_bathrooms",
            "num_carspaces",
            "city",
            "longitude",
            "latitude",
            "image_url",
            "indoor_features",
            "outdoor_features",
            "other_features",
            "description",
            "markdown",
            "created_at",
            "updated_at"
        ]


class ReadPropertyListingSerializer(serializers.ModelSerializer):
    estate = ReadPropertySerializer(read_only=True)
    property_type = ReadPropertyTypeSerializer(read_only=True)
    listing_type = ReadListingTypeSerializer(read_only=True)
    property_status = ReadPropertyStatusSerializer(read_only=True)

    class Meta:
        ref_name = "PropertyListingModel.read"
        model = PropertyListingModel
        fields = [
            "id",
            "listing_title",
            "listing_url",
            "estate",
            "property_type",
            "listing_type",
            "property_status",
            "price",
            "price_formatted",
            "is_delisted",
            "is_active",
            "created_at",
            "updated_at"
        ]
