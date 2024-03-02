from logging import getLogger
from rest_framework import serializers


logger = getLogger(__name__)


class UpdatePropertyWebhookSerializer(serializers.Serializer):
    json_fields = serializers.JSONField()

    class Meta:
        ref_field = "Scraper-api.update-property.request-body"
