"""
This module contains all string representations of the days of the week.
"""
from django.utils.translation import gettext_lazy as _

WEEKDAYS_LONG = [
    _("Monday"),
    _("Tuesday"),
    _("Wednesday"),
    _("Thursday"),
    _("Friday"),
    _("Saturday"),
    _("Sunday"),
]

WEEKDAYS_SHORT = [_("Mon"), _("Tue"), _("Wed"), _("Thu"), _("Fri"), _("Sat"), _("Sun")]
