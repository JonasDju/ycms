import logging

from ..models import Floor
from .custom_model_form import CustomModelForm

logger = logging.getLogger(__name__)


class FloorForm(CustomModelForm):
    """
    Form for creating floors
    """

    class Meta:
        """
        This class contains additional meta configuration of the form class, see the :class:`django.forms.ModelForm`
        for more information.
        """

        model = Floor
        fields = ["name", "code", "order", "predecessor", "successor"]
