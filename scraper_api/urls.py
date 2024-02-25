from django.urls import path
from .views.scraper_api_webhook_response_catcher import ScraperApiWebhookResponseCatcherAPIView

urlpatterns = [
    path("webhook/finished-job", ScraperApiWebhookResponseCatcherAPIView.as_view())
]
