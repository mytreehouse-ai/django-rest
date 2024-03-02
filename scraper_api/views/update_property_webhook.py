from logging import getLogger
from rest_framework.generics import UpdateAPIView
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema

from ..serializers.update_property_webhook_serializer import UpdatePropertyWebhookSerializer
from ..serializers.scraperapi_job_finished_response_serializer import ScraperApiWebhookJobFinishedResponseSerializer


logger = getLogger(__name__)


class UpdatePropertyWebhookaAPIView(UpdateAPIView):
    permission_classes = [HasAPIKey | IsAuthenticated]
    serializer_class = UpdatePropertyWebhookSerializer
    http_method_names = ["patch"]

    @swagger_auto_schema(
        operation_description="",
        operation_id="",
        request_body=UpdatePropertyWebhookSerializer(),
        responses={
            200: ScraperApiWebhookJobFinishedResponseSerializer()
        },
        tags=["Scrapy-job"],
    )
    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        print(serializer.validated_data)

        return Response(
            {
                "message": "Webhook response successfully processed."
            }
        )
