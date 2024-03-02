from logging import getLogger
from rest_framework import serializers

from ..models import ScrapyJobModel

logger = getLogger(__name__)


class ReadScrapyJobSerializer(serializers.ModelSerializer):
    class Meta:
        ref_name = 'ScrapyJobModel.read'
        model = ScrapyJobModel
        fields = [
            "id",
            "job_id",
            "domain",
            "status",
            "attempts",
            "status_url",
            "supposed_to_run_at",
            "single_page",
            "is_processed",
            "created_at",
            "updated_at"
        ]
