# Generated by Django 5.1.2 on 2024-10-26 12:06

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_rename_userasclient_client"),
        ("erp", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Client",
            new_name="ClientProfile",
        ),
    ]
