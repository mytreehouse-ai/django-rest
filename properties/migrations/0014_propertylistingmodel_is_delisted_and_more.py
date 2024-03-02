# Generated by Django 5.0.1 on 2024-03-02 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0013_alter_propertylistingmodel_listing_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='propertylistingmodel',
            name='is_delisted',
            field=models.BooleanField(default=False, verbose_name='Is Delisted'),
        ),
        migrations.AlterField(
            model_name='propertymodel',
            name='indoor_features',
            field=models.JSONField(blank=True, default=list, null=True, verbose_name='Indoor Features'),
        ),
        migrations.AlterField(
            model_name='propertymodel',
            name='other_features',
            field=models.JSONField(blank=True, default=list, null=True, verbose_name='Other Features'),
        ),
        migrations.AlterField(
            model_name='propertymodel',
            name='outdoor_features',
            field=models.JSONField(blank=True, default=list, null=True, verbose_name='Outdoor Features'),
        ),
    ]
