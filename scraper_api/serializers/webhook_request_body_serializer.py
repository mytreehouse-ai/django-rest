from logging import getLogger
from rest_framework import serializers

logger = getLogger(__name__)


class ScraperApiWebhookRequestBodySerializer(serializers.Serializer):
    """
    Serializer for the response of a webhook from the Scraper API.

    This serializer is used to serialize the response data received from the Scraper API webhook. It includes fields such as the job ID, number of attempts made, the status of the job, the status URL, the URL that was scraped, and the response body if the job has finished.

    Attributes:
        id (UUIDField): The unique identifier of the scraping job, in hex_verbose format. This field is read-only.
        attempts (IntegerField): The number of attempts made for the scraping job. This field is read-only and its value starts from 0.
        status (CharField): The current status of the scraping job, limited to 100 characters. This field is read-only.
        statusUrl (URLField): The URL to check the status of the scraping job. This field is read-only.
        url (URLField): The URL that was scraped. This field is read-only.
        response (SerializerMethodField): A method field that returns the response body of the scraping job if the job has finished.
    """

    id = serializers.UUIDField(format="hex_verbose")
    attempts = serializers.IntegerField(min_value=0)
    status = serializers.CharField(max_length=100)
    statusUrl = serializers.URLField()
    url = serializers.URLField()
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

    class Meta:
        ref_field = "Scraper-api.webhook.request-body"
