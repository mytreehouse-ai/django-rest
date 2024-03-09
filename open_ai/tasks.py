from logging import getLogger
from celery import shared_task
from django.core.cache import cache
from domain.models.city_model import CityModel

logger = getLogger(__name__)


@shared_task()
def update_available_cities_for_ai_context():
    """
    Update the cache with a comma-separated string of available city names.
    """
    try:
        cities = CityModel.objects.values_list('name', flat=True)
        cities_str = ', '.join(cities)
        cache.set(key="open_ai:cities_context", value=cities_str, timeout=None)
        logger.info("Cities cache updated successfully")
    except Exception as e:
        logger.error(f"Failed to update cities cache: {str(e)}")
