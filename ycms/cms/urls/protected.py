"""
URLconf for login-protected views of the cms package.
"""
from django.urls import include, path

from ..views import (
    authentication,
    floor,
    index,
    patients,
    timeline,
    user_settings_view,
    ward,
)
from ..views.utility.autocomplete import autocomplete_icd10, autocomplete_patient

urlpatterns = [
    path("", index.UserBasedRedirectView.as_view(), name="index"),
    path(
        "patients/",
        include(
            [
                path("", patients.PatientsListView.as_view(), name="patients"),
                path(
                    "<int:pk>/",
                    patients.PatientDetailsView.as_view(),
                    name="patient_details",
                ),
                path(
                    "create/",
                    patients.PatientCreateView.as_view(),
                    name="create_patient",
                ),
                path(
                    "record/<int:pk>/",
                    patients.RecordCreateView.as_view(),
                    name="create_record",
                ),
                path(
                    "update/<int:patient>/<int:bed_assignment>/",
                    patients.UpdatePatientStayView.as_view(),
                    name="update_patient_stay",
                ),
                path(
                    "update/<int:pk>/",
                    patients.PatientUpdateView.as_view(),
                    name="update_patient",
                ),
                path(
                    "delete/<int:pk>",
                    patients.PatientDeleteView.as_view(),
                    name="delete_patient",
                ),
                path(
                    "discharge/<int:assignment_id>/",
                    patients.DischargePatientView.as_view(),
                    name="discharge_patient",
                ),
                path(
                    "assign/<int:ward_id>/<int:assignment_id>/",
                    patients.AssignPatientView.as_view(),
                    name="assign_patient",
                ),
            ]
        ),
    ),
    path(
        "intake/",
        include(
            [
                path("", patients.IntakeFormView.as_view(), name="intake"),
                path(
                    "update/<int:pk>/",
                    patients.IntakeUpdateView.as_view(),
                    name="update_intake",
                ),
                path(
                    "cancel/<int:pk>/",
                    patients.PlannedStayCancelView.as_view(),
                    name="cancel_stay",
                ),
            ]
        ),
    ),
    path(
        "accounts/",
        include(
            [
                path(
                    "create-user/",
                    authentication.RegistrationView.as_view(),
                    name="create_user",
                )
            ]
        ),
    ),
    path(
        "autocomplete/",
        include(
            [
                path("icd10/", autocomplete_icd10, name="autocomplete_icd10"),
                path("patient/", autocomplete_patient, name="autocomplete_patient"),
            ]
        ),
    ),
    path(
        "ward/",
        include(
            [
                path("", ward.WardView.as_view(), name="ward_detail_default"),
                path("<int:pk>/", ward.WardView.as_view(), name="ward_detail"),
                path(
                    "manage/", ward.WardManagementView.as_view(), name="ward_management"
                ),
            ]
        ),
    ),
    path(
        "timeline/",
        include(
            [
                path(
                    "<int:pk>/suggest/",
                    timeline.TimelineView.as_view(),
                    name="timeline_suggest",
                ),
                path("<int:pk>/", timeline.TimelineView.as_view(), name="timeline"),
                path(
                    "mode-switch/<int:pk>/",
                    timeline.ModeSwitchView.as_view(),
                    name="mode_switch",
                ),
            ]
        ),
    ),
    path(
        "floor/",
        include(
            [
                path("", floor.FloorView.as_view(), name="floor"),
                path("create/", floor.FloorCreateView.as_view(), name="create_floor"),
                # path("update/<int:pk>/", floor.FloorUpdateView.as_view(), name="update_floor"),
                path("delete/<int:pk>", floor.FloorDeleteView.as_view(), name="delete_floor")
            ]
        ),
    ),
    path("settings/", user_settings_view.UserSettingsView.as_view(), name="settings"),
]
