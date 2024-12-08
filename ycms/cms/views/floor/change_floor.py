from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import DeleteView, TemplateView

from ...decorators import permission_required
from ...forms import FloorForm, FloorUpdateForm
from ...models import Floor


@method_decorator(permission_required("cms.change_floor"), name="dispatch")
class FloorCreateView(TemplateView):
    """
    View to add a floor
    """

    template_name = "floor/create_floor.html"

    def post(self, request, *args, **kwargs):
        r"""

        :param request: The current request
        :type request: ~django.http.HttpRequest

        :param \*args: The supplied arguments
        :type \*args: list

        :param \**kwargs: The supplied keyword arguments
        :type \**kwargs: dict

        :return: Redirect to floor view
        :rtype: ~django.http.HttpResponseRedirect
        """
        floor_form = FloorForm(
            data=request.POST, additional_instance_attributes={"creator": request.user}
        )
        if not floor_form.is_valid():
            floor_form.add_error_messages(request)
            return redirect("cms:protected:floor")
        floor = floor_form.save()
        messages.success(
            request, _('Floor "{}" was added successfully!').format(floor.name)
        )

        return redirect("cms:protected:floor")


@method_decorator(permission_required("cms.change_floor"), name="dispatch")
class FloorUpdateView(TemplateView):
    """
    View to add a floor
    """

    template_name = "floor/update_floor.html"
    # TODO(jan) do modal like id="assign-modal"
    # TODO(jan) delete modal (https://flowbite.com/blocks/application/crud-delete-confirm/) for floors wards and patients
    # TODO(jan) patients view -> load patients table entries on demand to improve speed

    def post(self, request, *args, **kwargs):
        r"""

        :param request: The current request
        :type request: ~django.http.HttpRequest

        :param \*args: The supplied arguments
        :type \*args: list

        :param \**kwargs: The supplied keyword arguments
        :type \**kwargs: dict

        :return: Redirect to floor view
        :rtype: ~django.http.HttpResponseRedirect
        """
        instance = Floor.objects.get(id=request.POST.get("id", None))

        floor_form = FloorUpdateForm(
            data=request.POST,
            additional_instance_attributes={"creator": request.user},
            instance=instance,
        )
        if not floor_form.is_valid():
            floor_form.add_error_messages(request)
            return redirect("cms:protected:floor")
        floor_form.save()
        messages.success(
            request,
            _('Floor "{}" was edited successfully!').format(floor_form.instance.name),
        )

        return redirect("cms:protected:floor")


@method_decorator(permission_required("cms.change_floor"), name="dispatch")
class FloorDeleteView(DeleteView):
    """
    View to delete a floor
    """

    model = Floor
    success_url = reverse_lazy("cms:protected:floor")

    def form_valid(self, form):
        messages.success(self.request, _("Floor has been deleted."))
        return super().form_valid(form)

    def form_invalid(self, form):
        form.add_error_messages(self.request)
        return redirect("cms:protected:floor")
