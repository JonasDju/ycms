"""
This module contains all string representations of all valid medical record types
"""
from django.utils.translation import gettext_lazy as _

INTAKE = "intake"
NOTE = "note"
LAB = "lab"

CHOICES = (
    (INTAKE, _("patient intake form")),
    (NOTE, _("note")),
    (LAB, _("lab report")),
)
