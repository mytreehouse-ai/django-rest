# Generated by Django 5.0.1 on 2024-03-11 00:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0022_alter_propertylistingmodel_vector_uuids'),
    ]

    operations = [
        migrations.AddField(
            model_name='propertylistingmodel',
            name='is_in_vector_table',
            field=models.BooleanField(default=False, verbose_name='Is In Vector Table'),
        ),
    ]
