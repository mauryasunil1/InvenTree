# Generated by Django 2.2.10 on 2020-04-04 12:38

from django.db import migrations


def create_thumbnails(apps, schema_editor):
    """
    Create thumbnails for all existing Part images.

    Note: This functionality is now performed in apps.py, 
    as running the thumbnail script here caused too many database level errors.

    This migration is left here to maintain the database migration history

    """
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('part', '0033_auto_20200404_0445'),
    ]

    operations = [
        migrations.RunPython(create_thumbnails, reverse_code=create_thumbnails),
    ]
