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
    response = serializers.SerializerMethodField()

    def get_response(self, obj):
        """
        Retrieves the response body of the scraping job if the job has finished.

        This method checks if the status of the job is 'finished'. If so, it returns the response body. Otherwise, it returns an empty dictionary.

        Args:
            obj (dict): The object instance representing the scraping job data.

        Returns:
            dict: A dictionary containing the 'body' of the response if the job has finished, otherwise an empty dictionary.
        """
        if obj.get('status') == 'finished':
            return {
                "body": obj.get('response', {}).get('body')
            }
        return {}
