# Generated by Django 5.1.2 on 2024-12-18 13:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_user_is_approved_tokensignup"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="is_approved",
            field=models.BooleanField(default=True, verbose_name="is approved"),
        ),
    ]