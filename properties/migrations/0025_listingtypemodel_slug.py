# Generated by Django 5.0.1 on 2024-03-16 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0024_alter_propertylistingmodel_price_formatted'),
    ]

    operations = [
        migrations.AddField(
            model_name='listingtypemodel',
            name='slug',
            field=models.CharField(max_length=200, null=True, verbose_name='Slug'),
        ),
    ]