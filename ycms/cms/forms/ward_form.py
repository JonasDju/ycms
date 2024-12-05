import logging

from ..models import Ward, Floor
from .custom_model_form import CustomModelForm

logger = logging.getLogger(__name__)


class WardForm(CustomModelForm):
    """
    Form for creating wards
    """

    class Meta:
        """
        This class contains additional meta configuration of the form class, see the :class:`django.forms.ModelForm`
        for more information.
        """

        model = Ward
        fields = ["name", "nickname", "floor"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["floor"].queryset = Floor.objects.order_by("-order")
        self.fields["floor"].label_from_instance = lambda obj: obj.name