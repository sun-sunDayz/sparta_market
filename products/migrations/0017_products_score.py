# Generated by Django 5.0.4 on 2024-04-19 13:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0016_remove_products_score_productrating"),
    ]

    operations = [
        migrations.AddField(
            model_name="products",
            name="score",
            field=models.FloatField(default=0),
        ),
    ]
