# Generated by Django 4.2.3 on 2023-11-07 13:24

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    The initial migration for this project.
    """

    initial = True

    dependencies = [("auth", "0012_alter_user_first_name_max_length")]

    operations = [
        migrations.CreateModel(
            name="User",
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
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "personnel_id",
                    models.CharField(
                        help_text="Employment ID number of the hospital staff. Used for authentication.",
                        max_length=10,
                        null=True,
                        unique=True,
                        validators=[django.core.validators.MinLengthValidator(10)],
                        verbose_name="personnel ID",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        help_text="Valid email address for this user",
                        max_length=254,
                        unique=True,
                        verbose_name="email",
                    ),
                ),
                (
                    "job_type",
                    models.CharField(
                        choices=[
                            ("ADMINISTRATOR", "Administrator"),
                            ("DOCTOR", "Dr."),
                            ("NURSE", "Nurse"),
                        ],
                        help_text="Job type of the employee",
                        max_length=16,
                        null=True,
                        verbose_name="job type",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        help_text="First name of the employee",
                        max_length=32,
                        null=True,
                        verbose_name="first name",
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        help_text="Last name of the employee",
                        max_length=64,
                        null=True,
                        verbose_name="last name",
                    ),
                ),
                ("is_active", models.BooleanField(default=True)),
                ("is_staff", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "ordering": ["personnel_id"],
                "default_permissions": ("change", "delete", "view"),
            },
        ),
        migrations.CreateModel(
            name="Bed",
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
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "bed_type",
                    models.CharField(
                        choices=[("normal", "normal")],
                        help_text="specialty bed types may be available",
                        max_length=10,
                        verbose_name="bed type",
                    ),
                ),
                (
                    "creator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"verbose_name": "bed", "verbose_name_plural": "beds"},
        ),
        migrations.CreateModel(
            name="ICD10Entry",
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
                    "code",
                    models.CharField(
                        help_text="ICD-10-GM classification code",
                        max_length=21,
                        verbose_name="code",
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        help_text="ICD-10-GM classification description",
                        max_length=256,
                        verbose_name="description",
                    ),
                ),
            ],
            options={
                "verbose_name": "ICD-10 entry",
                "verbose_name_plural": "ICD-10 entries",
            },
        ),
        migrations.CreateModel(
            name="Ward",
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
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "ward_number",
                    models.CharField(
                        help_text="Number of the ward",
                        max_length=32,
                        unique=True,
                        verbose_name="ward number",
                    ),
                ),
                (
                    "floor",
                    models.IntegerField(
                        help_text="Floor on which the nurse station for this ward is located",
                        verbose_name="floor",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Name this ward is commonly referred to by",
                        max_length=32,
                        verbose_name="ward name",
                    ),
                ),
                (
                    "creator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"verbose_name": "ward", "verbose_name_plural": "wards"},
        ),
        migrations.CreateModel(
            name="Room",
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
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "room_number",
                    models.CharField(
                        help_text="number of this room within its ward",
                        max_length=32,
                        verbose_name="room number",
                    ),
                ),
                (
                    "creator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "ward",
                    models.ForeignKey(
                        help_text="The ward this room belongs to",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rooms",
                        to="cms.ward",
                        verbose_name="ward",
                    ),
                ),
            ],
            options={"verbose_name": "room", "verbose_name_plural": "rooms"},
        ),
        migrations.CreateModel(
            name="Patient",
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
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "insurance_type",
                    models.BooleanField(
                        choices=[(False, "statutory"), (True, "private")],
                        default=False,
                        help_text="Whether the patient is privately insured or not",
                        verbose_name="insurance type",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        help_text="First name of the patient",
                        max_length=32,
                        verbose_name="first name",
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        help_text="Last name of the patient",
                        max_length=64,
                        verbose_name="last name",
                    ),
                ),
                (
                    "gender",
                    models.CharField(
                        choices=[("m", "male"), ("f", "female"), ("d", "diverse")],
                        help_text="Gender of the patient",
                        max_length=1,
                        verbose_name="gender",
                        default=None,
                    ),
                ),
                (
                    "date_of_birth",
                    models.DateField(
                        help_text="Date of birth of the patient",
                        verbose_name="date of birth",
                    ),
                ),
                ("_first", models.CharField(blank=True, max_length=32)),
                ("_last", models.CharField(blank=True, max_length=64)),
                (
                    "creator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"verbose_name": "patient", "verbose_name_plural": "patients"},
        ),
        migrations.CreateModel(
            name="MedicalRecord",
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
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "record_type",
                    models.CharField(
                        choices=[("intake", "patient intake form"), ("note", "note")],
                        help_text="type of this record",
                        max_length=32,
                        verbose_name="record type",
                    ),
                ),
                (
                    "note",
                    models.TextField(
                        blank=True,
                        help_text="Additional notes for this medical record",
                        verbose_name="note",
                    ),
                ),
                (
                    "creator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "diagnosis_code",
                    models.ForeignKey(
                        blank=True,
                        help_text="Diagnosis code according to ICD-10",
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="cms.icd10entry",
                        verbose_name="diagnosis code",
                    ),
                ),
                (
                    "patient",
                    models.ForeignKey(
                        help_text="The patient associated with this medical record",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="medical_records",
                        to="cms.patient",
                        verbose_name="patient",
                    ),
                ),
            ],
            options={
                "verbose_name": "medical record",
                "verbose_name_plural": "medical records",
                "get_latest_by": "-created_at",
            },
        ),
        migrations.CreateModel(
            name="BedAssignment",
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
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "admission_date",
                    models.DateField(
                        blank=True,
                        help_text="date the hostpital stay begins",
                        verbose_name="admission date",
                    ),
                ),
                (
                    "discharge_date",
                    models.DateField(
                        blank=True,
                        help_text="date the hospital stay ends",
                        null=True,
                        verbose_name="discharge date",
                    ),
                ),
                (
                    "accompanied",
                    models.BooleanField(
                        blank=True,
                        default=False,
                        help_text="Whether the patient is accompanied by a chaperone",
                        verbose_name="accompanied",
                    ),
                ),
                (
                    "bed",
                    models.ForeignKey(
                        blank=True,
                        help_text="The bed assigned to the patient",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="assignments",
                        to="cms.bed",
                        verbose_name="bed",
                    ),
                ),
                (
                    "creator",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "medical_record",
                    models.ForeignKey(
                        help_text="The medical record associated with this bed assignment",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bed_assignment",
                        to="cms.medicalrecord",
                        verbose_name="medical record",
                    ),
                ),
                (
                    "recommended_ward",
                    models.ForeignKey(
                        blank=True,
                        help_text="Recommendation for stay at this ward",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="cms.ward",
                        verbose_name="recommended ward",
                    ),
                ),
            ],
            options={
                "verbose_name": "bed assignment",
                "verbose_name_plural": "bed assignments",
            },
        ),
        migrations.AddField(
            model_name="bed",
            name="room",
            field=models.ForeignKey(
                help_text="The room this bed belongs to",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="beds",
                to="cms.room",
                verbose_name="room",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="assigned_ward",
            field=models.ForeignKey(
                blank=True,
                help_text="Ward this employee is assigned to (if any)",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="cms.ward",
                verbose_name="Ward",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="creator",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="groups",
            field=models.ManyToManyField(
                blank=True,
                help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                related_name="user_set",
                related_query_name="user",
                to="auth.group",
                verbose_name="groups",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="user_permissions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Specific permissions for this user.",
                related_name="user_set",
                related_query_name="user",
                to="auth.permission",
                verbose_name="user permissions",
            ),
        ),
    ]
