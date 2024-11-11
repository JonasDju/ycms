import logging

from ..models import Ward
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
        fields = ["ward_number", "floor", "name", "nickname"]
