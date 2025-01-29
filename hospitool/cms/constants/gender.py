"""
This module contains all string representations of all genders
"""
from django.utils.translation import gettext_lazy as _

MALE = "m"
FEMALE = "f"
DIVERSE = "d"

CHOICES = ((MALE, _("male")), (FEMALE, _("female")), (DIVERSE, _("diverse")))
