import logging
from django.core.management.base import BaseCommand

from properties.models.property_listing_model import PropertyListingModel
from properties.models.property_status_model import PropertyStatusModel

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    A Django management command that counts and prints the number of delisted property listings.

    This command extends BaseCommand and is designed to be executed from the command line or through Django's manage.py utility.
    It queries the PropertyListingModel to count how many property listings are marked as delisted and prints this count.
    """

    def handle(self, *args, **options):
        """
        The main entry point for the command. It counts the delisted property listings and prints the count.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments.
        """
        delisted = PropertyStatusModel.objects.get_or_create(
            description="Delisted"
        )

        is_delisted_count = PropertyListingModel.objects.filter(
            is_delisted=True,
            property_status=delisted
        ).count()

        print(f"is_delisted count: {is_delisted_count}")
