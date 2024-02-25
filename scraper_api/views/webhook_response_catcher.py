from logging import getLogger
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_yasg.utils import swagger_auto_schema

from ..serializers.webhook_request_body_serializer import ScraperApiWebhookRequestBodySerializer
from ..serializers.webhook_job_finished_response_serializer import ScraperApiWebhookJobFinishedResponseSerializer
from ..serializers.webhook_api_key_serializer import ScraperApiWebhookApiKeySerializer
from ..services.scraperapi_service import ScrapyJobService


logger = getLogger(__name__)


class WebhookResponseCatcherAPIView(CreateAPIView):
    """
    API view to catch and process webhook responses from the Scraper API.

    This view extends the CreateAPIView to provide a method for handling POST requests. 
    It is designed to receive webhook responses from the Scraper API, deserialize the data using 
    the ScraperApiWebhookResponseSerializer, and perform necessary actions based on the received data.

    Attributes:
        serializer_class (Serializer): The serializer class used for request data validation and deserialization. Set to ScraperApiWebhookResponseSerializer.

    Methods:
        post(request, *args, **kwargs): Handles POST requests. It deserializes the request data, validates it, and processes the webhook response as needed.
    """
    permission_classes = [AllowAny]
    serializer_class = ScraperApiWebhookRequestBodySerializer

    @swagger_auto_schema(
        operation_description="Catches and processes webhook responses from the Scraper API.",
        operation_id="catch_scraper_api_webhook_response",
        request_body=ScraperApiWebhookRequestBodySerializer(),
        responses={
            200: ScraperApiWebhookJobFinishedResponseSerializer()
        },
        tags=["Scrapy-job"],
    )
    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to catch and process webhook responses from the Scraper API.

        It uses the ScraperApiWebhookResponseSerializer to deserialize and validate the request data. After validation, 
        it extracts necessary information such as job ID, attempts, status, and response from the validated data. 
        This information can then be used to perform further processing or logging.

        Args:
            request (Request): The request object containing the webhook data.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Response: A DRF Response object with a message indicating the result of the operation.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job_id = serializer.validated_data.get("id")
        attempts = serializer.validated_data.get("attempts")
        status = serializer.validated_data.get("status")
        failed_reason = serializer.validated_data.get("failedReason", None)
        response = serializer.validated_data.get("response", None)

        scrapy_job_service = ScrapyJobService()

        print({
            "job_id": job_id,
            "attempts": attempts,
            "status": status,
            "html_code": response.get("body", None) if response else None,
            "failed_reason": failed_reason
        })

        scrapy_job_service.update_job(
            job_id=job_id,
            attempts=attempts,
            status=status,
            html_code=response.get("body", None) if response else None,
            failed_reason=failed_reason
        )

        return Response(
            {
                "message": "Webhook response successfully processed."
            }
        )
