# Generated by Django 5.1.2 on 2024-12-19 12:13

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_alter_user_is_approved"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="tokensignup",
            options={
                "verbose_name": "Token (Sign-up)",
                "verbose_name_plural": "Tokens (Sign-up)",
            },
        ),
    ]
