# Generated by Django 5.0.1 on 2024-03-02 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0015_propertymodel_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='propertymodel',
            name='markdown',
            field=models.TextField(blank=True, null=True, verbose_name='Markdown'),
        ),
    ]
