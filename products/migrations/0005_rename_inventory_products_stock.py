# Generated by Django 5.0.4 on 2024-04-16 09:56

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("products", "0004_products_hits_products_likey_products_score_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="products",
            old_name="inventory",
            new_name="stock",
        ),
    ]