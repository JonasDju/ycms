# Generated by Django 4.2.8 on 2024-12-05 00:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("cms", "0011_alter_floor_order")]

    operations = [
        migrations.AlterField(
            model_name="floor",
            name="code",
            field=models.CharField(
                help_text="Shortname of the floor",
                max_length=10,
                unique=True,
                verbose_name="floor code",
            ),
        ),
        migrations.AlterField(
            model_name="floor",
            name="name",
            field=models.CharField(
                help_text="Name of the floor",
                max_length=30,
                unique=True,
                verbose_name="floor name",
            ),
        ),
    ]
