"""
This module contains all string representations of all valid insurance types
"""
from django.utils.translation import gettext_lazy as _

STATUTORY = False
PRIVATE = True

CHOICES = ((STATUTORY, _("statutory")), (PRIVATE, _("private")))
