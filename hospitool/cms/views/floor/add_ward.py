from django.contrib import messages
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import TemplateView

from ...decorators import permission_required
from ...forms import WardForm
from ...models import Floor


@method_decorator(permission_required("cms.change_floor"), name="dispatch")
class WardCreateView(TemplateView):
    """
    View to add a war from floor view
    """

    template_name = "floor/create_ward.html"

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
        data = {k: v for k, v in request.POST.items()}
        data["floor"] = Floor.objects.get(pk=request.POST["floor_id"])
        ward_form = WardForm(
            data=data, additional_instance_attributes={"creator": request.user}
        )
        if not ward_form.is_valid():
            ward_form.add_error_messages(request)
            return redirect("cms:protected:floor")
        ward = ward_form.save()
        messages.success(
            request, _('Ward "{}" was added successfully!').format(ward.name)
        )

        return redirect("cms:protected:ward_details", pk=ward.id)
