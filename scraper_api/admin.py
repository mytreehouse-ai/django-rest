from django.contrib import admin

# Register your models here.
from .models import ScrapyJobModel

@admin.register(ScrapyJobModel)
class ScrapyJobModelAdmin(admin.ModelAdmin):
    list_display = (
        "id", "job_id", "domain", "status", "attempts", "status_url", 
        "supposed_to_run_at", "is_processed", "finished_processed_at", 
        "failed_reason", "html_code", "created_at", "updated_at"
    )