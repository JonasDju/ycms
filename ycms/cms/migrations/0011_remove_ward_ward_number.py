# Generated by Django 4.2.8 on 2024-11-22 17:15

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("cms", "0010_alter_ward_nickname")]

    operations = [migrations.RemoveField(model_name="ward", name="ward_number")]
