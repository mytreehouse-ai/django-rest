import os
import json
import requests
from time import sleep
from logging import getLogger
from bs4 import BeautifulSoup
from celery import shared_task
from django.utils import timezone

from .services.scraperapi_service import ScrapyJobService
from .serializers.create_scrapy_job_serializer import CreateScrapyJobSerializer
from properties.models.property_type_model import PropertyTypeModel
from properties.models.property_status_model import PropertyStatusModel
from properties.models.listing_type_model import ListingTypeModel
from properties.models.property_listing_model import PropertyListingModel
from properties.models.property_model import PropertyModel


logger = getLogger(__name__)


@shared_task()
def scraperapi_process_scrapy_web():
    """
    Initiates scraping jobs for each page of every Scrapy web entity.

    This function iterates through all Scrapy web entities retrieved from the database
    and sends a POST request to the ScraperAPI for each page of each Scrapy web entity.
    It constructs a payload containing the API key, the URL to scrape (with page number),
    and a callback webhook URL. After sending the request, it processes the response,
    creating a new Scrapy job in the database with the response data or logs an error
    if the response cannot be parsed as JSON or if the ScraperAPI returns an error status code.
    """
    scrapy_webs = ScrapyJobService.get_all_scrapy_web()

    for scrapy_web in scrapy_webs:
        for i in range(1, scrapy_web.page_number + 1):
            payload = {
                "apiKey": os.environ.get("SCRAPER_API_KEY"),
                "url": f"{scrapy_web.web_url}/?page={i}",
                "callback": {
                    "type": "webhook",
                    "url": f"{os.environ.get('DJANGO_API_URL')}/scrapy-jobs/webhook/finished-job"
                }
            }

            endpoint = "https://async.scraperapi.com/jobs"

            response = requests.post(
                endpoint,
                json=payload,
                headers={
                    "Content-Type": "application/json"
                }
            )

            try:
                response_json: CreateScrapyJobSerializer = response.json()
                job = {
                    "job_id": response_json.get("id", None),
                    "domain": response_json.get("url", None),
                    "status": response_json.get("status", None),
                    "attempts": response_json.get("attempts", None),
                    "status_url": response_json.get("status_url", None),
                    "supposed_to_run_at": response_json.get("supposedToRunAt", None)
                }
                ScrapyJobService.create_job(**job)
            except ValueError:
                logger.error("Failed to parse response as JSON.")
                response_json = "Invalid JSON response"
            if response.status_code == 200:
                logger.info(
                    f"Scraping job started successfully. Response: {response_json}"
                )
            else:
                logger.error(
                    f"Failed to start scraping job. Status code: {response.status_code}, Response: {response_json}"
                )

            # Sleep for 1 second after each page iteration to avoid overwhelming the server
            sleep(1)


@shared_task()
def scraperapi_job_checker():
    pass


@shared_task()
def lamudi_scraper():
    property_details = []

    def get_attribute(element, attribute):
        value = element.attrs.get(attribute, '')
        return 'n/a' if not value else value

    def extract_html(html_data: str):
        soup = BeautifulSoup(html_data, 'html.parser')
        info_elements = soup.find_all(class_='ListingCell-AllInfo ListingUnit')
        return info_elements

    scrapy_jobs = ScrapyJobService.get_all_scrapy_job()

    current_scrapy_job_id = None
    for_sale = PropertyListingModel.objects.get(id=1)
    for_rent = PropertyListingModel.objects.get(id=2)
    condominium = PropertyTypeModel.objects.get(id=1)
    house = PropertyTypeModel.objects.get(id=2)
    apartment = PropertyTypeModel.objects.get(id=3)
    warehouse = PropertyTypeModel.objects.get(id=4)
    land = PropertyTypeModel.objects.get(id=5)

    for scrapy_job in scrapy_jobs:
        current_scrapy_job_id = scrapy_job.id

        info_elements = extract_html(html_data=scrapy_job.html_code)
        for element in info_elements:
            category = get_attribute(element, 'data-category')
            details_dict = {
                'listing_title': element.find('a', class_='js-listing-link')['title'] if element.find('a', class_='js-listing-link') else 'n/a',
                'price': float(get_attribute(element, 'data-price')) if get_attribute(element, 'data-price') != 'n/a' else 'n/a',
                # Seen in warehouse
                'price_condition': get_attribute(element, 'data-price_conditions'),
                'category': category,
                'subcategories': json.loads(get_attribute(element, 'data-subcategories')),
                'year_built': get_attribute(element, 'data-year_built'),
                'condo_name': get_attribute(element, 'data-condominiumname'),
                # For warehouse
                'subdivision_name': get_attribute(element, 'data-subdivisionname'),
                'car_spaces': int(get_attribute(element, 'data-car_spaces')) if get_attribute(element, 'data-car_spaces').isdigit() else 'n/a',
                'bedrooms': int(get_attribute(element, 'data-bedrooms')) if get_attribute(element, 'data-bedrooms').isdigit() else 'n/a',
                'bathrooms': int(get_attribute(element, 'data-bathrooms')) if get_attribute(element, 'data-bathrooms').isdigit() else 'n/a',
                # floor area
                'building_size': float(get_attribute(element, 'data-building_size')) if get_attribute(element, 'data-building_size') != 'n/a' else 0.0,
                # sqm
                'land_size': float(get_attribute(element, 'data-land_size')) if get_attribute(element, 'data-land_size') != 'n/a' else 0.0,
                'furnished': get_attribute(element, 'data-furnished'),
                'classification': get_attribute(element, 'data-classification'),
                'block': get_attribute(element, 'data-block'),
                'subdivision_name': get_attribute(element, 'data-subdivisionname'),
                'sku': get_attribute(element, 'data-sku'),
                'geo_point': [
                    float(coord.strip('[]')) for coord in get_attribute(element, 'data-geo-point').split(',')
                ] if get_attribute(element, 'data-geo-point') != 'n/a' else 'n/a',
                'listing_url': element.find('a', class_='js-listing-link')['href'] if element.find('a', class_='js-listing-link') else None
            }

            property_details.append(details_dict)

    if current_scrapy_job_id:
        scrapy_job = ScrapyJobService.get_scrapy_job(id=current_scrapy_job_id)

        scrapy_job.html_code = None
        scrapy_job.is_processed = True
        scrapy_job.finished_processed_at = timezone.now()
        scrapy_job.save(
            update_fields=[
                "html_code",
                "is_processed",
                "finished_processed_at"
            ]
        )

        current_scrapy_job_id = None

    for property in property_details:
        if property.get("category") == "commercial":
            # Ensure price does not cause numeric field overflow
            price = min(property.get("price", 0), 999999999999.99)
            new_listing, created = PropertyListingModel.objects.get_or_create(
                listing_title=property.get("listing_title"),
                defaults={
                    'listing_url': property.get("listing_url"),
                    'property_type': warehouse,
                    'price': price,
                    'is_active': True
                }
            )
            if created:
                # Extract geo_point safely
                geo_point = property.get("geo_point", [None, None])
                longitude = geo_point[0] if len(geo_point) > 0 else 0.0
                latitude = geo_point[1] if len(geo_point) > 1 else 0.0

                new_warehouse = PropertyModel.objects.create(
                    subdivision_name=property.get("subdivision_name", None),
                    lot_size=property.get("land_size", None),
                    building_size=property.get("building_size", None),
                    longitude=longitude,
                    latitude=latitude
                )

                new_listing.estate = new_warehouse
                new_listing.save(update_fields=["estate"])

                print(f"New listing added: {new_listing.listing_url}")
            else:
                print(f"Listing already exists: {new_listing.listing_url}")

        sleep(1)

    property_details = []
