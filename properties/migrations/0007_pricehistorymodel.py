# Generated by Django 5.0.1 on 2024-02-28 01:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0006_alter_propertylistingmodel_property_status_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PriceHistoryModel',
            fields=[
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('price', models.DecimalField(decimal_places=2, max_digits=12, verbose_name='Price')),
                ('date_recorded', models.DateTimeField(auto_now_add=True, verbose_name='Date Recorded')),
                ('property_listing', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='price_histories', to='properties.propertylistingmodel', verbose_name='Property Listing')),
            ],
            options={
                'verbose_name': 'Price History',
                'verbose_name_plural': 'Price Histories',
                'db_table': 'price_histories',
                'ordering': ['-date_recorded'],
            },
        ),
    ]
