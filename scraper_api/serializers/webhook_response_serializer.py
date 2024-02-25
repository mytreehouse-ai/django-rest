from logging import getLogger
from rest_framework import serializers

logger = getLogger(__name__)


class ScraperApiWebhookResponseSerializer(serializers.Serializer):
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
