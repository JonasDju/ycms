from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic.edit import DeleteView

from ...decorators import permission_required
from ...forms import WardForm
from ...models import Ward


@method_decorator(permission_required("cms.delete_ward"), name="dispatch")
class WardDeleteView(DeleteView):
    """
    View to delete a ward
    """

    model = Ward
    success_url = reverse_lazy("cms:protected:ward_management")

    def form_valid(self, form):
        messages.success(self.request, _("Ward has been deleted."))
        return super().form_valid(form)

    def form_invalid(self, form):
        form.add_error_messages(self.request)
        return redirect("cms:protected:ward_management")
