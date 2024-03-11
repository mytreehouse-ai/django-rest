import os
import time
from logging import getLogger
from celery import shared_task
from django.core.cache import cache

from domain.models.city_model import CityModel
from properties.models.property_listing_model import PropertyListingModel
from open_ai.services.apollo_exploration.service import ApolloExplorationService

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


@shared_task()
def update_vector_property_listings():
    apollo_exporation_service = ApolloExplorationService(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    pg_vector = apollo_exporation_service.pg_vector(
        collection_name="property_listings"
    )

    property_listings = PropertyListingModel.objects.filter(
        is_in_vector_table=False,
        is_active=True,
        estate__description__isnull=False
    ).order_by('-id')[:10]

    for property_listing in property_listings:
        estate = f"""
            [{property_listing.listing_title}]({property_listing.listing_url})
            Price: {property_listing.price_formatted}
            Listing type: {property_listing.listing_type.description}
            Property type: {property_listing.property_type.description}
            Lot size: {property_listing.estate.lot_size}
            Floor size: {property_listing.estate.floor_size}
            Building size: {property_listing.estate.building_size}
            Address: {property_listing.estate.address}
            City: {property_listing.estate.city.name}
            Building name: {property_listing.estate.building_name}
            Subdivision name: {property_listing.estate.subdivision_name}
            Bedrooms: {property_listing.estate.num_bedrooms}
            Bathrooms: {property_listing.estate.num_bathrooms}
            Parking space: {property_listing.estate.num_carspaces}
            Indoor feature: {property_listing.estate.indoor_features}
            Outdoor feature: {property_listing.estate.outdoor_features}
            Other Feature: {property_listing.estate.other_features}
            Description: {property_listing.estate.description}
            """

        print(estate)

        documents = apollo_exporation_service.get_text_chunks_langchain(
            text=estate
        )
        customs_ids = pg_vector.add_documents(documents=documents)

        property_listing.vector_uuids = customs_ids
        property_listing.is_in_vector_table = True
        property_listing.save(
            update_fields=[
                "vector_uuids",
                "is_in_vector_table"
            ]
        )

        logger.info(
            f"Property stored in vector database with property id: {property_listing.id}"
        )

        time.sleep(30)
