import logging

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from ...decorators import permission_required
from ...forms import IntakeBedAssignmentForm, PatientForm, RecordForm
from ...models import BedAssignment, MedicalRecord, Patient

logger = logging.getLogger(__name__)


@method_decorator(permission_required("cms.view_patient"), name="dispatch")
class PatientDetailsView(TemplateView):
    """
    View to see all information about a single patient
    and their medical history
    """

    template_name = "patients/patient_details.html"

    def get_context_data(self, **kwargs):
        """
        This function returns all data about a patient.

        :param kwargs: The supplied keyword arguments
        :type kwargs: dict

        :return: Response for filtered offers
        :rtype: ~django.template.response.TemplateResponse
        """
        patient = get_object_or_404(Patient, pk=kwargs["pk"])
        return {
            "patient": patient,
            "patient_form": PatientForm(instance=patient, prefix=kwargs["pk"]),
            "record_form": RecordForm(user=self.request.user),
            "current_stay_forms": (
                RecordForm(instance=patient.current_stay.medical_record, user=self.request.user),
                IntakeBedAssignmentForm(instance=patient.current_stay),
            )
            if patient.current_stay
            else None,
            "planned_stays": [
                (
                    stay,
                    (
                        RecordForm(instance=stay.medical_record, user=self.request.user),
                        IntakeBedAssignmentForm(instance=stay),
                    ),
                )
                for stay in BedAssignment.objects.filter(
                    medical_record__patient=patient, admission_date__gt=timezone.now()
                )
            ],
            "records": MedicalRecord.objects.filter(patient=patient).order_by(
                "-created_at"
            ),
            **super().get_context_data(**kwargs),
        }


@method_decorator(permission_required("cms.add_patient"), name="dispatch")
class RecordCreateView(CreateView):
    """
    View to create a record
    """

    model = MedicalRecord
    form_class = RecordForm

    def form_valid(self, form):
        form.instance.creator = self.request.user
        form.instance.patient_id = self.kwargs["pk"]
        form.save()
        messages.success(self.request, _("New record has been created."))
        return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))

    def form_invalid(self, form):
        form.add_error_messages(self.request)
        return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))


@method_decorator(permission_required("cms.change_patient"), name="dispatch")
class IntakeUpdateView(UpdateView):
    """
    View to update a hospital stay
    """

    model = MedicalRecord
    form_class = RecordForm

    def form_valid(self, form):
        bed_assignment_form = IntakeBedAssignmentForm(
            instance=form.instance.bed_assignment.get(),
            data=self.request.POST,
            additional_instance_attributes={"is_update": True},
        )
        if not bed_assignment_form.is_valid():
            return self.form_invalid(bed_assignment_form)
        
        # check if user is allowed to modify diagnosis
        user = self.request.user
        if not (user.is_superuser or user.job_type == "DOCTOR"):
            # replace incoming diagnosis_code with old value
            form.instance.diagnosis_code = self.get_object().diagnosis_code

        form.save()
        bed_assignment_form.save()
        messages.success(
            self.request,
            _("Hospital stay for patient {}, {} has been updated.").format(
                form.instance.patient.last_name, form.instance.patient.first_name
            ),
        )
        return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))

    def form_invalid(self, form):
        form.add_error_messages(self.request)
        return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))


@method_decorator(permission_required("cms.change_patient"), name="dispatch")
class PlannedStayCancelView(DeleteView):
    """
    View to cancel (delete) a planned hospital stay
    """

    model = BedAssignment

    def form_valid(self, _form):
        self.object.delete()
        messages.success(self.request, _("The planned stay has been canceled."))
        return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))

    def form_invalid(self, form):
        form.add_error_messages(self.request)
        return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))
