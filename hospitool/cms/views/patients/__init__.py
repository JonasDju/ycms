"""
This package contains views related to patients
"""
from .assign_view import AssignPatientView
from .discharge_view import DischargePatientView
from .intake_form_view import IntakeFormView
from .patient_details_view import (
    IntakeUpdateView,
    PatientDetailsView,
    PlannedStayCancelView,
    RecordCreateView,
)
from .patients_list_view import (
    PatientCreateView,
    PatientDeleteView,
    PatientsListView,
    PatientUpdateView,
    UploadDataView,
)
from .update_patient_stay_view import UpdatePatientStayView
