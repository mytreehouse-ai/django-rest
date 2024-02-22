from logging import getLogger
from rest_framework.generics import CreateAPIView
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from ..serializers.create_scrapy_job_serializer import CreateScrapyJobSerializer
from ..serializers.read_scrapy_job_serializer import ReadScrapyJobSerializer
from ..services.scraperapi_service import ScrapyJobService

logger = getLogger(__name__)


class CreateScrapyJobWebhookAPIView(CreateAPIView):
    permission_classes = [HasAPIKey | IsAuthenticated]
    serializer_class = CreateScrapyJobSerializer

    @swagger_auto_schema(
        request_body=CreateScrapyJobSerializer(),
        responses={201: ReadScrapyJobSerializer},
        operation_description="Create a new user from a webhook. Requires API key authentication.",
        operation_id="create_user_from_webhook",
        tags=["Scrapy-job"],
        security=[{"ApiKeyAuth": []}]
    )
    def post(self, request, *args, **kwargs):
        request_data_serializer = self.get_serializer(data=request.data)
        request_data_serializer.is_valid(raise_exception=True)

        job_id = request_data_serializer.validated_data.get("id")
        attempts = request_data_serializer.validated_data.get("attempts")
        status = request_data_serializer.validated_data.get("status")
        status_url = request_data_serializer.validated_data.get("statusUrl")
        url = request_data_serializer.validated_data.get("url")
        supposed_to_run_at = request_data_serializer.validated_data.get(
            "supposedToRunAt"
        )

        scrapy_job_service = ScrapyJobService()

        scrapy_job_service.create_job({
            "job_id": job_id,
            "attempts": attempts,
            "status": status,
            "status_url": status_url,
            "url": url,
            "supposed_to_run_at": supposed_to_run_at
        })
