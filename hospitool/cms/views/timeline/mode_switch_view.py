import logging

from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic.edit import UpdateView

from ...decorators import permission_required
from ...models import User

logger = logging.getLogger(__name__)


@method_decorator(permission_required("cms.change_patient"), name="dispatch")
class ModeSwitchView(UpdateView):
    """
    View to the mode in which a user sees wards
    """

    model = User
    fields = ["ward_as_timeline"]

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            "cms:protected:ward_detail", kwargs={"pk": self.kwargs.get("pk", None)}
        )
