"""
This module contains all string representations of all valid bed types
"""
from django.utils.translation import gettext_lazy as _

NORMAL = "normal"
SMALL = "small"

CHOICES = ((NORMAL, _("normal")), (SMALL, _("small")))
