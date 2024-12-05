# Generated by Django 4.2.8 on 2024-12-02 09:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("cms", "0010_floor_alter_ward_floor")]

    operations = [
        migrations.AlterField(
            model_name="floor",
            name="order",
            field=models.IntegerField(
                help_text="Order of the floor", unique=True, verbose_name="floor order"
            ),
        )
    ]
