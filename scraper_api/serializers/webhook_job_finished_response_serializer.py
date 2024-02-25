from logging import getLogger
from rest_framework import serializers

logger = getLogger(__name__)


class ScraperApiWebhookJobFinishedResponseSerializer(serializers.Serializer):
    """
    A serializer for handling the response of a finished job from the Scraper API webhook.

    This serializer is primarily used for serializing the response data sent to clients
    after a scraping job has been completed. It includes a single field, `message`, which
    contains a summary or result of the scraping job.

    Methods:
        create(validated_data): Creates a new instance of the response. This method is a placeholder
        and does not implement actual creation logic, as the serializer is intended for serialization purposes only.

        update(instance, validated_data): Updates an existing instance of the response with new data.
        This method is a placeholder and does not implement actual update logic, as the serializer is
        intended for serialization purposes only.
    """

    message = serializers.CharField(max_length=255)

    def create(self, validated_data):
        """
        Create and return a new `WebhookResponse` instance, given the validated data.
        """
        # This is a placeholder for actual creation logic.
        # Since this serializer might be used just for serialization and not for creating an instance,
        # the implementation details are omitted.
        return validated_data

    def update(self, instance, validated_data):
        """
        Update and return an existing `WebhookResponse` instance, given the validated data.
        """
        # This is a placeholder for actual update logic.
        # Since this serializer might be used just for serialization and not for updating an instance,
        # the implementation details are omitted.
        instance['message'] = validated_data.get(
            'message', instance['message']
        )
        return instance

    class Meta:
        ref_field = "Scraper-api.webhook.job-finished-response"
