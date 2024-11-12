"""
This package contains all data models of YCMS.
Please refer to :mod:`django.db.models` for general information about Django models.
"""
from .bed import Bed
from .bed_assignment import BedAssignment
from .floor import Floor
from .icd10_entry import ICD10Entry
from .medical_record import MedicalRecord
from .patient import Patient
from .room import Room
from .user import User
from .ward import Ward
