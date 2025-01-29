import logging

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from django.core.paginator import Paginator
from django.db.models import Value
from django.db.models.functions import Concat

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

        context = super().get_context_data(**kwargs)

        search = self.request.GET.get("search")
        if search:
            patients_list = Patient.objects.prefetch_related("medical_records").annotate(full_name=Concat('last_name', Value(', '), 'first_name')).filter(full_name__icontains=search).order_by("-updated_at")
        else:
            patients_list = Patient.objects.prefetch_related("medical_records").all().order_by("-updated_at")

        paginator = Paginator(patients_list, 10)  # Show 10 patients per page

        page_number = self.request.GET.get("page")  # Get the current page number from the query string
        page_obj = paginator.get_page(page_number)  # Get the patients for the current page

        context.update({
            "patients": page_obj,  # The paginated patients
            "new_patient_form": PatientForm(),
            "upload_csv_form": UploadCSVForm(),
        })
        return context

@method_decorator(permission_required("cms.add_patient"), name="dispatch")
class UploadDataView(FormView):
    """
    View to upload data of patients and their stays
    """

    success_url = reverse_lazy("cms:protected:patients")
    form_class = UploadCSVForm

    def form_valid(self, form):
        csv_file = form.cleaned_data['file']
        data_to_import = form.cleaned_data['selected_categories']
        import_result = import_data(
            csv_file=csv_file,
            user=self.request.user,
            data_to_import=data_to_import,
            val_sep=","
        )
        error_code = import_result["error_code"]
        error_msg = import_result["error_msg"]
        new_entries = import_result["new_entry_count"]
        duplicate_entries = import_result["duplicate_entry_count"]
        updated_entries = import_result["updated_entry_count"]

        if error_code == None:
            messages.success(
                self.request,
                _("Data was successfully imported."),
            )
            messages.info(
                self.request,
                _("New patients added: {}").format(new_entries),
            )
            messages.info(
                self.request,
                _("Duplicated entries found: {}").format(duplicate_entries)
            )
            messages.info(
                self.request,
                _("Entries updated: {}").format(updated_entries)
            )
        else:
            messages.error(
                self.request,
                error_msg,
            )
            messages.info(
                self.request,
                _("No entries were added or updated."),
            )

        return super().form_valid(form)

    def form_invalid(self, form):
        # alternative approach, if original Django errors should not be presented to the user
        """
        if any("csv" in error for error in form.errors['file']):
            messages.error(self.request, _("Only files with extension .csv are allowed."))
        else:
            messages.error(self.request, _("An error occured while uploading the file."))
        """
        for field in form.errors:
            for error in field:
                messages.error(self.request, error)
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
