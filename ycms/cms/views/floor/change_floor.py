from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import DeleteView, TemplateView

from ...decorators import permission_required
from ...forms import FloorForm
from ...models import Floor


@method_decorator(permission_required("cms.change_floor"), name="dispatch")
class FloorCreateView(TemplateView):
    """
    View to add a floor
    """

    template_name = "floor/create_floor.html"
    # TODO(jan) use CreateView instead, see patients_list_view.py
    # TODO(jan) edit floor view, delete modal (https://flowbite.com/blocks/application/crud-delete-confirm/)
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
        floor_form = FloorForm(
            data=request.POST, additional_instance_attributes={"creator": request.user}
        )
        if not floor_form.is_valid():
            floor_form.add_error_messages(request)
            return render(
                request,
                self.template_name,
                {
                    "floor_form": floor_form,
                    "floors": Floor.objects.all(),
                    **super().get_context_data(**kwargs),
                },
            )
        floor = floor_form.save()
        messages.success(
            request, _('Addition of new floor "{}" successful!').format(floor.name)
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
