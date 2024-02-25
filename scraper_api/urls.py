from django.urls import path
from .views.webhook_response_catcher import WebhookResponseCatcherAPIView

urlpatterns = [
    path("webhook/finished-job", WebhookResponseCatcherAPIView.as_view())
]
