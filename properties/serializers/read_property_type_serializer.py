from logging import getLogger
from rest_framework import serializers

from ..models.property_type_model import PropertyTypeModel

logger = getLogger(__name__)


class ReadPropertyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        # TODO: Empty ref_name
        ref_name = ""
        model = PropertyTypeModel
        fields = [
            "id",
            "description"
        ]
