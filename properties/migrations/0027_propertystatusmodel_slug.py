# Generated by Django 5.0.1 on 2024-03-16 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0026_alter_listingtypemodel_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='propertystatusmodel',
            name='slug',
            field=models.CharField(max_length=200, null=True, verbose_name='Slug'),
        ),
    ]
