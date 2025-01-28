"""
This module contains all string representations of all valid bed blocking types
"""
from django.utils.translation import gettext_lazy as _

NOTBLOCKED = "NOTBLOCKED"
DOCTORSHORTAGE = "DOCTORSHORTAGE"
DOCTORCAREGIVERSHORTAGE = "DOCTORCAREGIVERSHORTAGE"
NOTOPERATED = "NOTOPERATED"
INFECTIOUS = "INFECTIOUS"
CONSTRUCTION = "CONSTRUCTION"
RESERVED = "RESERVED"
MEDREASON = "MEDREASON"
PALLIATIVE = "PALLIATIVE"
CAREGIVERSHORTAGE = "CAREGIVERSHORTAGE"
OS = "OS"
OSSRL = "OSSRL"
OSSRS = "OSSRS"
OSRR = "OSRR"
FRANZISKUS = "FRANZISKUS"

CHOICES = (
    (NOTBLOCKED, _("-------")), 
    (DOCTORSHORTAGE, _("Shortage of doctors")),
    (DOCTORCAREGIVERSHORTAGE, _("Shortage of doctors and caregivers")),
    (NOTOPERATED, _("Currently not in operation")),
    (INFECTIOUS, _("Infectious")),
    (CONSTRUCTION, _("Construction/repair")),
    (RESERVED, _("Reserved for patient")),
    (MEDREASON, _("Med. reason/incompliance")),
    (PALLIATIVE, _("Palliative")),
    (CAREGIVERSHORTAGE, _("Shortage of caregivers")),
    (OS, _("Optional service")),
    (OSSRL, _("OS SR large")),
    (OSSRS, _("OS SR small")),
    (OSRR, _("OS room rate")),
    (FRANZISKUS, _("Franziskus")),
)