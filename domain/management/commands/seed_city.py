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
                city_name = re.sub(r'[\ufffd\u00f1\u00d1]',
                                   'ñ', row[2]).capitalize()

                _, created = CityModel.objects.get_or_create(
                    name=city_name
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(
                        f'Successfully added city {city_name}'))
                else:
                    self.stdout.write(self.style.WARNING(
                        f'City {city_name} already exists'))
