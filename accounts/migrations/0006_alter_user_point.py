# Generated by Django 5.0.4 on 2024-04-18 19:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0005_rename_garde_user_grade"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="point",
            field=models.IntegerField(default=500),
        ),
    ]
