# Generated by Django 5.0.1 on 2024-03-10 06:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0019_alter_propertylistingmodel_listing_title_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='propertylistingmodel',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=19, verbose_name='Price'),
        ),
    ]
