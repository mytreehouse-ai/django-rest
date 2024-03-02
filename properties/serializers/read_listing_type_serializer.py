from logging import getLogger
from rest_framework import serializers

from ..models.listing_type_model import ListingTypeModel

logger = getLogger(__name__)


class ReadListingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingTypeModel
        fields = [
            "id",
            "description"
        ]
