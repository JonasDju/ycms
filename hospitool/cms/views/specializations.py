import logging

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from ..decorators import permission_required
from ..forms import MedicalSpecializationForm
from ..models import MedicalSpecialization

logger = logging.getLogger(__name__)


@method_decorator(permission_required("cms.change_medicalspecialization"), name="dispatch")
class SpecializationsListView(TemplateView):
    """
    View to see all specializations and add a new one
    """

    template_name = "specializations_list.html"

    def get_context_data(self, **kwargs):
        """
        This function returns a list of all specializations.

        :param kwargs: The supplied keyword arguments
        :type kwargs: dict

        :return: Response for filtered offers
        :rtype: ~django.template.response.TemplateResponse
        """
        return {
            "specializations": [
                (specialization, MedicalSpecializationForm(instance=specialization, prefix=specialization.id))
                for specialization in MedicalSpecialization.objects.all().order_by("name")
            ],
            "new_specialization_form": MedicalSpecializationForm(),
        }


@method_decorator(permission_required("cms.add_medicalspecialization"), name="dispatch")
class SpecializationCreateView(CreateView):
    """
    View to create a medical specialization
    """

    model = MedicalSpecialization
    success_url = reverse_lazy("cms:protected:specializations")
    form_class = MedicalSpecializationForm

    def form_valid(self, form):
        messages.success(
            self.request,
            _("Specialization {} ({}) has been created.").format(
                form.instance.name, form.instance.abbreviation
            ),
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        form.add_error_messages(self.request)
        return redirect("cms:protected:specializations")


@method_decorator(permission_required("cms.change_medicalspecialization"), name="dispatch")
class SpecializationUpdateView(UpdateView):
    """
    View to update a medical specialization
    """

    model = MedicalSpecialization
    form_class = MedicalSpecializationForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"prefix": self.kwargs["pk"]})
        return kwargs

    def form_valid(self, form):
        messages.success(
            self.request,
            _("Specialization {} ({}) has been updated.").format(
                form.instance.name, form.instance.abbreviation
            ),
        )
        form.save()
        return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))

    def form_invalid(self, form):
        form.add_error_messages(self.request)
        return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))


@method_decorator(permission_required("cms.delete_medicalspecialization"), name="dispatch")
class SpecializationDeleteView(DeleteView):
    """
    View to delete a medical specialization
    """

    model = MedicalSpecialization
    success_url = reverse_lazy("cms:protected:specializations")

    def form_valid(self, form):
        messages.success(
            self.request, 
            _("Specialization {} ({}) has been deleted.").format(
                self.get_object().name, self.get_object().abbreviation
                ),
            )
        return super().form_valid(form)

    def form_invalid(self, form):
        form.add_error_messages(self.request)
        return redirect("cms:protected:specializations")