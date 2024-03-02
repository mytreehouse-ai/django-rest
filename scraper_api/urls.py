from django.urls import path
from .views.read_scrapy_job_webhook import ReadScrapyJobWebhookAPIView
from .views.scraperapi_catcher_webhook import ScraperapiCatcherWebhookAPIView
from .views.update_property_webhook import UpdatePropertyWebhookAPIView

urlpatterns = [
    path("webhook/finished-job", ScraperapiCatcherWebhookAPIView.as_view()),
    path("webhook/scrapy-jobs", ReadScrapyJobWebhookAPIView.as_view()),
    path("webhook/property", UpdatePropertyWebhookAPIView.as_view())
]
