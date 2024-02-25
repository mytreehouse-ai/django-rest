from logging import getLogger
from rest_framework.generics import UpdateAPIView
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from ..serializers.update_scrapy_job_webhook_serializer import UpdateScraperJobWebhookSerializer
from ..services.scraperapi_service import ScrapyJobService

logger = getLogger(__name__)


class UpdateScrapyJobWebhookAPIView(UpdateAPIView):
    permission_classes = [HasAPIKey | IsAuthenticated]
    serializer_class = UpdateScraperJobWebhookSerializer
    http_method_names = ["patch"]

    @swagger_auto_schema(
        operation_description="Updates a Scrapy job's status via webhook. Requires either API key or user authentication.",
        operation_id="update_scrapy_job_status",
        request_body=UpdateScraperJobWebhookSerializer(),
        responses={
            200: {
                "message": "Job status updated successfully"
            },
        },
        tags=["Scrapy-job"],
    )
    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job_id = serializer.validated_data.get("id")
        attempts = serializer.validated_data.get("attempts")
        status = serializer.validated_data.get("status")
        failed_reason = serializer.validated_data.get("failedReason", None)
        response = serializer.validated_data.get("response", None)

        scrapy_job_service = ScrapyJobService()
        scrapy_job_service.update_job(
            job_id=job_id,
            attempts=attempts,
            status=status,
            html_code=response,
            failed_reason=failed_reason
        )

        return Response(
            {
                "message": "Job status updated successfully"
            },
            status=200
        )
