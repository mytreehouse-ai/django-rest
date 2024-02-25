from logging import getLogger
from rest_framework import serializers

logger = getLogger(__name__)


class UpdateScraperJobWebhookSerializer(serializers.Serializer):
    """
    Serializer for updating a Scrapy job via webhook.
    This serializer defines the structure of the webhook request body for updating the status of a Scrapy job.
    It handles both "finished" and "failed" statuses, including the response property for "finished" and the failedReason for "failed".
    """
    id = serializers.UUIDField(format="hex_verbose", required=True)
    status = serializers.ChoiceField(
        choices=["finished", "failed"],
        required=True
    )
    statusUrl = serializers.URLField(required=False)
    url = serializers.URLField(required=True)
    failedReason = serializers.CharField(required=False)
    response = serializers.JSONField()

    class Meta:
        ref_field = "Scraper-api.webhook.update"
