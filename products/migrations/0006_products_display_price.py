# Generated by Django 5.0.4 on 2024-04-17 15:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0005_rename_inventory_products_stock"),
    ]

    operations = [
        migrations.AddField(
            model_name="products",
            name="display_price",
            field=models.IntegerField(default=0),
        ),
    ]
