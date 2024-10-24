# Generated by Django 5.1.2 on 2024-10-24 13:36

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Counterparty",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("inn", models.CharField(max_length=12, unique=True)),
                ("name", models.CharField(max_length=255)),
                ("guid", models.CharField(max_length=36, unique=True)),
            ],
            options={
                "verbose_name": "Counterparty",
                "verbose_name_plural": "Counterparties",
            },
        ),
        migrations.CreateModel(
            name="ConstructionObject",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("code", models.CharField(max_length=255)),
                ("guid", models.CharField(max_length=36)),
                (
                    "counterparty",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="erp.counterparty",
                    ),
                ),
            ],
            options={
                "verbose_name": "Construction object",
                "verbose_name_plural": "Construction objects",
            },
        ),
    ]
