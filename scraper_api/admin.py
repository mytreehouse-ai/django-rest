from django.contrib import admin

from .models import ScrapyJobModel, ScrapyWebModel


@admin.register(ScrapyJobModel)
class ScrapyJobModelAdmin(admin.ModelAdmin):
    list_display = (
        "id", "job_id", "domain", "status", "attempts", "status_url",
        "supposed_to_run_at", "is_processed", "finished_processed_at",
        "failed_reason", "html_code", "created_at", "updated_at"
    )
    search_fields = ("domain", "status")


@admin.register(ScrapyWebModel)
class ScrapyWebModel(admin.ModelAdmin):
    list_display = ("web_url", "page_number", "created_at", "updated_at")
    search_fields = ("web_url",)
