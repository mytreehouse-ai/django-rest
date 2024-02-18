from logging import getLogger
from rest_framework import serializers

logger = getLogger(__name__)


class CreateScrapyJobSerializer(serializers.Serializer):
    """
    Serializer for creating a Scrapy job.
    This serializer defines the structure of the request body for creating a new Scrapy job.
    """
    id = serializers.UUIDField(format="hex_verbose", read_only=True)
    attempts = serializers.IntegerField(min_value=0, default=0, read_only=True)
    status = serializers.CharField(
        max_length=100,
        default="running",
        read_only=True
    )
    statusUrl = serializers.URLField(read_only=True)
    url = serializers.URLField()
    supposedToRunAt = serializers.DateTimeField()
