# Generated by Django 5.1.2 on 2024-10-26 11:21

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_userasclient"),
        ("erp", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="UserAsClient",
            new_name="Client",
        ),
    ]
