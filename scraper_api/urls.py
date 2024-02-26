from django.urls import path
from .views.response_catcher_webhook import ResponseCatcherWebhookAPIView

urlpatterns = [
    path("webhook/finished-job", ResponseCatcherWebhookAPIView.as_view())
]
