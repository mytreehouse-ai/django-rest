from django.urls import path
from .views.read_scrapy_job import ReadScrapyJobAPIView
from .views.response_catcher_webhook import ResponseCatcherWebhookAPIView

urlpatterns = [
    path("webhook/finished-job", ResponseCatcherWebhookAPIView.as_view()),
    path("webhook/scrapy-jobs", ReadScrapyJobAPIView.as_view())
]
