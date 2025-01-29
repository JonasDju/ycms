"""
This module contains the possible job types of employees to make them translatable.
"""
from django.utils.translation import gettext_lazy as _

ADMINISTRATOR = "ADMINISTRATOR"
DOCTOR = "DOCTOR"
NURSE = "NURSE"

CHOICES = [(ADMINISTRATOR, _("Administrator")), (DOCTOR, _("Dr.")), (NURSE, _("Nurse"))]
