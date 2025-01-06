"""
Forms for creating and modifying database objects.
Please refer to :mod:`django.forms` for general information about Django forms (see also: :doc:`django:topics/forms/index`).
"""
from .authentication.password_reset_request_form import PasswordResetRequestForm
from .authentication.registration_form import RegistrationForm
from .floor_form import FloorForm, FloorUpdateForm
from .intake_bed_assignment_form import IntakeBedAssignmentForm
from .intake_record_form import IntakeRecordForm
from .patient_form import PatientForm
from .patients.record_form import RecordForm
from .unknown_patient_form import UnknownPatientForm
from .user_form import UserForm
from .ward_form import WardForm
from .room_form import RoomForm
from .bed_form import BedForm
