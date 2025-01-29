"""
This module contains the possible names of roles to make them translatable.
"""
from django.utils.translation import gettext_lazy as _

ZBM = "ZBM"
STATION_MANAGEMENT = "STATION_MANAGEMENT"
MEDICAL_PERSONNEL = "MEDICAL_PERSONNEL"

MEDICAL_PERSONNEL_CAN_CREATE = []
STATION_MANAGEMENT_CAN_CREATE = MEDICAL_PERSONNEL_CAN_CREATE + [
    (MEDICAL_PERSONNEL, _("Medical Personnel"))
]
ZBM_CAN_CREATE = STATION_MANAGEMENT_CAN_CREATE + [
    (STATION_MANAGEMENT, _("Station Management"))
]

CHOICES = ZBM_CAN_CREATE + [(ZBM, _("Central Bed Management"))]

IS_CREATABLE_BY = {
    MEDICAL_PERSONNEL: MEDICAL_PERSONNEL_CAN_CREATE,
    STATION_MANAGEMENT: STATION_MANAGEMENT_CAN_CREATE,
    ZBM: ZBM_CAN_CREATE,
}

DEFAULT_VIEWS = {
    ZBM: "cms:protected:ward_management",
    STATION_MANAGEMENT: "cms:protected:ward_detail_default",
    MEDICAL_PERSONNEL: "cms:protected:patients",
}
