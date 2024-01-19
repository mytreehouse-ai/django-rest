from django.db import models
from management.models.base_model import BaseModel

class ScrapyJobModel(BaseModel):
    id = models.AutoField(primary_key=True)
    job_id = models.CharField(max_length=100, unique=True, blank=False)
    domain = models.CharField(max_length=100, unique=False, blank=False)
    status = models.CharField(max_length=100, default="Pending")

    def __str__(self) -> str:
        return self.domain

    class Meta:
        db_table = "scrapy_jobs"
        verbose_name = "Scrapy job"
        verbose_name_plural = "Scrapy jobs"
        ordering = ["id"]
