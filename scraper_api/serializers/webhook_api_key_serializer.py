from logging import getLogger
from rest_framework import serializers

logger = getLogger(__name__)


class ScraperApiWebhookApiKeySerializer(serializers.Serializer):
    api_key = serializers.CharField(
        max_length=255,
        required=True,
        help_text="API key for authentication"
    )
