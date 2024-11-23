import logging

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import TemplateView

from ...decorators import permission_required
from ...forms import (
    IntakeBedAssignmentForm,
    IntakeRecordForm,
    PatientForm,
    UnknownPatientForm,
)
from ...models import Patient
from ...models.timetravel_manager import current_or_travelled_time

logger = logging.getLogger(__name__)


@method_decorator(permission_required("cms.add_patient"), name="dispatch")
class IntakeFormView(TemplateView):
    """
    View to perform intake on new or existing patients
    """

    template_name = "patients/patient_intake_form.html"

    def get_context_data(self, **kwargs):
        """
        This function returns a list of all patients,
        as well as a form for creating a new one

        :param kwargs: The supplied keyword arguments
        :type kwargs: dict

        :return: Response for filtered offers
        :rtype: ~django.template.response.TemplateResponse
        """
        context = super().get_context_data(**kwargs)

        initial_patient = None
        if (patient_id := self.request.GET.get("patient")) and (
            patient := Patient.objects.get(pk=patient_id)
        ):
            initial_patient = patient

        context.update(
            {
                "patient_form": PatientForm(),
                "unknown_patient_form": UnknownPatientForm(),
                "record_form": IntakeRecordForm(initial_patient=initial_patient),
                "bed_form": IntakeBedAssignmentForm(),
            }
        )
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        r"""
        Submit :class:`~ycms.cms.forms.patients.patient_form.PatientForm`

        :param request: The current request
        :type request: ~django.http.HttpRequest

        :param \*args: The supplied arguments
        :type \*args: list

        :param \**kwargs: The supplied keyword arguments
        :type \**kwargs: dict

        :return: Redirect to list of patients
        :rtype: ~django.http.HttpResponseRedirect
        """
        # Get the existing patient or create a new one
        if patient_id := request.POST.get("patient"):
            patient = Patient.objects.get(id=patient_id)
            patient_form = PatientForm()
        else:
            form_type = (
                UnknownPatientForm
                if "unknown-approximate_age" in request.POST
                else PatientForm
            )
            patient_form = form_type(
                data=request.POST,
                additional_instance_attributes={"creator": request.user},
            )
            if not patient_form.is_valid():
                patient_form.add_error_messages(request)
                return render(
                    request,
                    self.template_name,
                    self.get_context_data(**kwargs) | {"patient_form": patient_form},
                )

            patient = patient_form.save()

            messages.success(
                request,
                _('Patient "{} {}" has been saved.').format(
                    patient.first_name, patient.last_name
                ),
            )

        # Create a new medical record for the patient
        record_form = IntakeRecordForm(
            data=request.POST,
            additional_instance_attributes={
                "creator": request.user,
                "selected_patient": patient,
            },
        )

        if not record_form.is_valid():
            record_form.add_error_messages(request)
            return render(
                request,
                self.template_name,
                self.get_context_data(**kwargs)
                | {"patient_form": patient_form, "record_form": record_form},
            )

        record = record_form.save()

        # Create a new bed assignment for the medical record
        bed_form = IntakeBedAssignmentForm(
            data=request.POST,
            additional_instance_attributes={
                "creator": request.user,
                "medical_record": record,
            },
        )

        if not bed_form.is_valid():
            bed_form.add_error_messages(request)
            return render(
                request,
                self.template_name,
                self.get_context_data(**kwargs)
                | {
                    "patient_form": patient_form,
                    "record_form": record_form,
                    "bed_form": bed_form,
                },
            )

        bed_assignment = bed_form.save()

        messages.success(
            request,
            _('Intake for patient "{} {}" with diagnosis "{}" has been saved.').format(
                patient.first_name, patient.last_name, record.diagnosis_code
            ),
        )

        if (
            bed_assignment.recommended_ward
            and bed_assignment.admission_date <= current_or_travelled_time()
        ):
            kwargs = {"pk": bed_assignment.recommended_ward.id}
            return HttpResponseRedirect(
                f"{reverse('cms:protected:ward_detail', kwargs=kwargs)}?drawer=drawer-right-unassigned"
            )
        return redirect("cms:protected:patient_details", pk=patient.id)
