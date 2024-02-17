from logging import getLogger
from django.db import models
from domain.models.base_model import BaseModel

logger = getLogger(__name__)


class ScrapyWebModel(BaseModel):
    """
    ScrapyWebModel stores information about web pages to be scraped.

    This model keeps track of the URLs that need to be scraped, along with their
    pagination information and active status. It inherits from the BaseModel,
    which provides it with created_at and updated_at fields.

    Attributes:
        id (AutoField): The primary key for the web page entry.
        web_url (URLField): The URL of the web page to be scraped. It is unique to avoid duplicate scraping tasks.
        page_number (IntegerField): The current page number to be scraped, useful for paginated websites. Defaults to 1.
        is_active (BooleanField): Flag indicating whether the web page is active for scraping. Defaults to True.
    """

    id = models.AutoField(primary_key=True)
    web_url = models.URLField(unique=True)
    page_number = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        """
        Returns the web URL of the Scrapy web model instance as its string representation.

        Returns:
            str: The web URL of the instance.
        """
        return self.web_url

    class Meta:
        db_table = "scrapy_webs"
        verbose_name = "Scrapy web"
        verbose_name_plural = "Scrapy webs"
        ordering = ["-id"]
