# Generated by Django 5.1.2 on 2024-12-24 08:05

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0005_alter_orderconfig_max_date"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderconfig",
            name="notification_on_statues",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(
                    choices=[
                        ("created", "создана"),
                        ("accepted", "принята"),
                        ("cancelled", "отменена"),
                        ("on_confirm", "на согласовании"),
                    ],
                    max_length=100,
                ),
                blank=True,
                null=True,
                size=None,
            ),
        ),
    ]
