import json
import logging
from decimal import Decimal
from django.utils import timezone
from django.core.management.base import BaseCommand

from properties.services.property_valuation_service import PropertyValuationService

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    A Django management command that calculates and prints the valuation of a condominium property.

    This command is designed to be executed from the command line or through Django's manage.py utility.
    It utilizes the PropertyValuationService to calculate the valuation based on predefined parameters
    such as city_id, year_built, and floor_area.
    """

    def handle(self, *args, **options):
        """
        The main entry point for the command. It calculates the condominium valuation and prints it.

        Args:
            *args: Variable length argument list.
            **options: Arbitrary keyword arguments.

        This method fetches the current year, subtracts 10 to simulate a building that is 10 years old,
        and uses a fixed city_id and floor_area to calculate the condominium's valuation. The result is
        then printed in a JSON formatted string.
        """
        city_id = 1990  # Taguig
        year_built = timezone.now().year - 10  # Assuming the building is 10 years old
        service = PropertyValuationService()
        condominium_valuation = service.condominium(
            floor_area=100,
            city_id=city_id,
            year_built=year_built
        )
        # Convert Decimal values to float for JSON serialization
        condominium_valuation = {
            k: float(v) if isinstance(
                v, Decimal
            ) else v for k, v in condominium_valuation.items()
        }
        print(json.dumps(condominium_valuation, indent=4))
