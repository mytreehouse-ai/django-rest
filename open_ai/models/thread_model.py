from logging import getLogger
from django.db import models
from domain.models.base_model import BaseModel

logger = getLogger(__name__)


class ThreadModel(BaseModel):
    id = models.AutoField(
        primary_key=True
    )
    thread_id = models.CharField(
        max_length=100,
        unique=True,
        blank=False
    )
    thread_title = models.CharField(
        max_length=100,
        unique=True,
        blank=False
    )

    def __str__(self) -> str:
        return self.thread_title

    class Meta:
        db_table = "threads"
        verbose_name = "Thread"
        verbose_name_plural = "Threads"
        ordering = ["id"]
