import logging

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import TemplateView

from ...decorators import permission_required
from ...forms import IntakeBedAssignmentForm, PatientForm
from ...models import BedAssignment, Patient

logger = logging.getLogger(__name__)


@method_decorator(permission_required("cms.change_patient"), name="dispatch")
class UpdatePatientStayView(TemplateView):
    """
    View to update a patient's detail and their most recent hospital stay
    """

    template_name = "patients/patient_card_wrapper.html"

    def get(self, request, *args, **kwargs):
        """
        This function returns forms for updating
        a patient and their current bed assignment

        :param request: The current request
        :type request: ~django.http.HttpRequest

        :param args: The supplied arguments
        :type args: list

        :param kwargs: The supplied keyword arguments
        :type kwargs: dict

        :return: Response for filtered offers
        :rtype: ~django.template.response.TemplateResponse
        """
        patient = get_object_or_404(Patient, id=kwargs.get("patient"))
        bed_assignment = get_object_or_404(
            BedAssignment, id=kwargs.get("bed_assignment")
        )
        return render(
            request,
            self.template_name,
            {
                "patient": patient,
                "patient_form": PatientForm(instance=patient),
                "bed_assignment": bed_assignment,
                "bed_assignment_form": IntakeBedAssignmentForm(
                    instance=bed_assignment,
                    additional_instance_attributes={"creator": bed_assignment.creator},
                ),
                **super().get_context_data(**kwargs),
            },
        )

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        r"""
        Submit :class:`~hospitool.cms.forms.patients.patient_form.PatientForm`
           and :class:`~hospitool.cms.forms.patients.intake_bed_assignment_form.IntakeBedAssignmentForm`

        :param request: The current request
        :type request: ~django.http.HttpRequest

        :param \*args: The supplied arguments
        :type \*args: list

        :param \**kwargs: The supplied keyword arguments
        :type \**kwargs: dict

        :return: Redirect to list of patients
        :rtype: ~django.http.HttpResponseRedirect
        """
        patient = get_object_or_404(Patient, id=kwargs.get("patient"))
        patient_form = PatientForm(data=request.POST, instance=patient)

        bed_assignment = get_object_or_404(
            BedAssignment, id=kwargs.get("bed_assignment")
        )
        bed_assignment_form = IntakeBedAssignmentForm(
            data=request.POST,
            instance=bed_assignment,
            additional_instance_attributes={"is_update": True},
        )

        if not patient_form.is_valid() or not bed_assignment_form.is_valid():
            patient_form.add_error_messages(request)
            bed_assignment_form.add_error_messages(request)
            return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

        patient = patient_form.save()
        bed_assignment = bed_assignment_form.save()

        messages.success(
            request,
            _(
                'Patient "{} {}"  and their current stay from {} to {} have been saved.'
            ).format(
                patient.first_name,
                patient.last_name,
                bed_assignment.admission_date,
                bed_assignment.discharge_date,
            ),
        )

        return HttpResponseRedirect(request.META.get("HTTP_REFERER"))
