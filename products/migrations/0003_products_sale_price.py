# Generated by Django 5.0.4 on 2024-04-15 18:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0002_products_inventory"),
    ]

    operations = [
        migrations.AddField(
            model_name="products",
            name="sale_price",
            field=models.IntegerField(default=0),
        ),
    ]
