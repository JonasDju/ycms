import logging

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView

from ...decorators import permission_required
from ...forms import PatientForm, UploadCSVForm
from ...models import Patient

from ...import_data import import_data

logger = logging.getLogger(__name__)


@method_decorator(permission_required("cms.view_patient"), name="dispatch")
class PatientsListView(TemplateView):
    """
    View to see all patients and add a new one
    """

    template_name = "patients/patients_list.html"

    def get_context_data(self, **kwargs):
        """
        This function returns a list of all patients.

        :param kwargs: The supplied keyword arguments
        :type kwargs: dict

        :return: Response for filtered offers
        :rtype: ~django.template.response.TemplateResponse
        """
        return {
            "patients": [
                (patient, PatientForm(instance=patient, prefix=patient.id))
                for patient in Patient.objects.prefetch_related("medical_records")
                .all()
                .order_by("-updated_at")
            ],
            "new_patient_form": PatientForm(),
            "upload_csv_form": UploadCSVForm(),
            **super().get_context_data(**kwargs),
        }

@method_decorator(permission_required("cms.add_patient"), name="dispatch")
class UploadDataView(FormView):
    """
    View to upload data of patients and their stays 
    """

    success_url = reverse_lazy("cms:protected:patients")
    form_class = UploadCSVForm
    
    def form_valid(self, form):
        csv_file = form.cleaned_data['file']
        import_result = import_data(csv_file=csv_file, user=self.request.user, val_sep=",")
        import_error = import_result["error"]
        p_count, dc_count = import_result["patient_count"], import_result["diagnosis_code_count"]
        mr_count, ba_count = import_result["medical_record_count"], import_result["bed_assignment_count"]

        if import_error == None:
            if sum ([p_count, dc_count, mr_count, ba_count]) > 0:
                messages.success(
                    self.request,
                    _("Data was successfully imported."),
                )
                messages.info(
                    self.request,
                    _("New patients: {}").format(p_count),
                )
                messages.info(
                    self.request,
                    _("New diagnosis codes: {}").format(dc_count),
                )
                messages.info(
                    self.request,
                    _("New medical records: {}").format(mr_count),
                )
                messages.info(
                    self.request,
                    _("New bed assignments: {}").format(ba_count),
                )
            else:
                messages.info(
                    self.request,
                    _("No new entries were found in CSV file.")
                )
                messages.info(
                    self.request,
                    _("No new entries were created."),
                )
        elif import_error == -1:
            messages.error(
                self.request,
                _("The CSV file could not be read."),
            )
            messages.info(
                self.request,
                _("No new entries were created."),
            )
        elif import_error == -2:
            messages.error(
                self.request,
                _("The CSV file does not contain all required column labels."),
            )
            messages.info(
                self.request,
                _("No new entries were created."),
            )
        else:
            messages.error(
                self.request,
                _("An error occured when importing entry no. {}.").format(
                    import_error
                ),
            )
            messages.info(
                self.request,
                _("No new entries were created."),
            )
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, _("An error occured while uploading the file."))
        return redirect("cms:protected:patients")

@method_decorator(permission_required("cms.add_patient"), name="dispatch")
class PatientCreateView(CreateView):
    """
    View to create a patient
    """

    model = Patient
    success_url = reverse_lazy("cms:protected:patients")
    form_class = PatientForm

    def form_valid(self, form):
        form.instance.creator = self.request.user
        messages.success(
            self.request,
            _("Patient {}, {} has been created.").format(
                form.instance.last_name, form.instance.first_name
            ),
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        form.add_error_messages(self.request)
        return redirect("cms:protected:patients")


@method_decorator(permission_required("cms.change_patient"), name="dispatch")
class PatientUpdateView(UpdateView):
    """
    View to update a patient
    """

    model = Patient
    form_class = PatientForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"prefix": self.kwargs["pk"]})
        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request,
            _("Patient {}, {} has been updated.").format(
                form.instance.last_name, form.instance.first_name
            ),
        )
        form.save()
        return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))

    def form_invalid(self, form):
        form.add_error_messages(self.request)
        return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))


@method_decorator(permission_required("cms.change_patient"), name="dispatch")
class PatientDeleteView(DeleteView):
    """
    View to delete a patient
    """

    model = Patient
    success_url = reverse_lazy("cms:protected:patients")

    def form_valid(self, form):
        messages.success(self.request, _("Patient has been deleted."))
        return super().form_valid(form)

    def form_invalid(self, form):
        form.add_error_messages(self.request)
        return redirect("cms:protected:patients")
