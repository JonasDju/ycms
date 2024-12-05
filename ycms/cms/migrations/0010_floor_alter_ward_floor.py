# Generated by Django 4.2.8 on 2024-11-11 06:59

import django.db.models.deletion
from django.db import migrations, models

import ycms.cms.models.timetravel_manager


class Migration(migrations.Migration):
    dependencies = [("cms", "0009_rename_discharge_date")]

    operations = [
        migrations.CreateModel(
            name="Floor",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        default=ycms.cms.models.timetravel_manager.current_or_travelled_time
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "name",
                    models.CharField(
                        help_text="Name of the floor",
                        max_length=30,
                        null=True,
                        verbose_name="floor name",
                    ),
                ),
                (
                    "code",
                    models.CharField(
                        help_text="Shortname of the floor",
                        max_length=10,
                        null=True,
                        verbose_name="floor code",
                    ),
                ),
                (
                    "order",
                    models.IntegerField(
                        help_text="Order of the floor",
                        verbose_name="floor order",
                    ),
                ),
            ],
            options={"verbose_name": "floor", "verbose_name_plural": "floors"},
        ),
        migrations.AlterField(
            model_name="ward",
            name="floor",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="cms.floor"
            ),
        ),
    ]
