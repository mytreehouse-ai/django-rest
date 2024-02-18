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
    response = serializers.JSONField(required=False)

    def validate(self, data):
        """
        Custom validation to ensure that 'response' is provided for "finished" status
        and 'failedReason' is provided for "failed" status.
        """
        if data["status"] == "finished" and "response" not in data:
            raise serializers.ValidationError(
                {"response": "This field is required for status 'finished'."})
        if data["status"] == "failed":
            if "failedReason" not in data:
                raise serializers.ValidationError(
                    {"failedReason": "This field is required for status 'failed'."})
            # Ensure 'response' is not included for "failed" status
            if "response" in data:
                raise serializers.ValidationError(
                    {"response": "This field should not be included for status 'failed'."})
        return data
