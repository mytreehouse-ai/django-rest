from logging import getLogger
from rest_framework import serializers

logger = getLogger(__name__)


class ScraperApiWebhookResponseHeadersSerializer(serializers.Serializer):
    date = serializers.CharField(required=False)
    content_type = serializers.CharField(required=False)
    content_length = serializers.CharField(required=False)
    connection = serializers.CharField(required=False)
    x_powered_by = serializers.CharField(required=False)
    access_control_allow_origin = serializers.CharField(required=False)
    access_control_allow_headers = serializers.CharField(required=False)
    access_control_allow_methods = serializers.CharField(required=False)
    access_control_allow_credentials = serializers.CharField(required=False)
    x_robots_tag = serializers.CharField(required=False)
    set_cookie = serializers.ListField(
        child=serializers.CharField(), required=False
    )
    sa_final_url = serializers.CharField(required=False)
    sa_statuscode = serializers.CharField(required=False)
    sa_credit_cost = serializers.CharField(required=False)
    sa_proxy_hash = serializers.CharField(required=False)
    etag = serializers.CharField(required=False)
    vary = serializers.CharField(required=False)
    strict_transport_security = serializers.CharField(required=False)


class ScraperApiWebhookResponseBodySerializer(serializers.Serializer):
    headers = ScraperApiWebhookResponseHeadersSerializer(required=False)
    body = serializers.CharField(required=False)
    statusCode = serializers.IntegerField(required=False)
    credits = serializers.IntegerField(required=False)

    class Meta:
        ref_field = "Scraper-api.webhook.response-body"


class ScraperApiWebhookRequestBodySerializer(serializers.Serializer):
    """
    Serializer for the response of a webhook from the Scraper API.

    This serializer is used to serialize the response data received from the Scraper API webhook. 
    It includes fields such as the job ID, number of attempts made, the status of the job, the status URL, 
    the URL that was scraped, and the response body if the job has finished.

    Attributes:
        id (UUIDField): The unique identifier of the scraping job, in hex_verbose format. This field is read-only.
        attempts (IntegerField): The number of attempts made for the scraping job. This field is read-only and its value starts from 0.
        status (CharField): The current status of the scraping job, limited to 100 characters. This field is read-only.
        statusUrl (URLField): The URL to check the status of the scraping job. This field is read-only.
        url (URLField): The URL that was scraped. This field is read-only.
        response (JSONField): A JSON field that contains the response body of the scraping job if the job has finished.
    """

    id = serializers.UUIDField(format="hex_verbose")
    attempts = serializers.IntegerField(min_value=0)
    status = serializers.CharField(max_length=100)
    statusUrl = serializers.URLField()
    failedReason = serializers.CharField(required=False)
    url = serializers.URLField()
    response = ScraperApiWebhookResponseBodySerializer(required=False)

    class Meta:
        ref_field = "Scraper-api.webhook.request-body"

    class Meta:
        ref_field = "Scraper-api.webhook.request-body"
