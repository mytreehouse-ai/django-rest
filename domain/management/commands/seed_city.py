import re
import csv
from django.core.management.base import BaseCommand
from domain.models.city_model import CityModel


class Command(BaseCommand):
    help = 'Seed cities from CSV file'

    def handle(self, *args, **options):
        with open('domain/csv/refcitymun.csv', mode='r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                city = re.sub(r'[\ufffd\u00f1]', 'ñ', row[2])

                _, created = CityModel.objects.get_or_create(
                    city.capitalize()
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f'Successfully added city {city}'))
                else:
                    self.stdout.write(self.style.WARNING(
                        f'City {city} already exists'))
