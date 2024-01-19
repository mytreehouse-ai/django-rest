import logging
from django.db import models

logger = logging.getLogger(__name__)

class BaseModel(models.Model):
    """
    Abstract base class for models, providing timestamp fields for creation and last update.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Meta class to declare the model as abstract.
        """
        abstract = True
