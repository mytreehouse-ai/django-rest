from logging import getLogger
from rest_framework import serializers

from ..models.property_status_model import PropertyStatusModel

logger = getLogger(__name__)


class ReadPropertyStatusSerializer(serializers.ModelSerializer):
    class Meta:
        # TODO: Empty ref_name
        ref_name = ""
        model = PropertyStatusModel
        fields = [
            "id",
            "description"
        ]
