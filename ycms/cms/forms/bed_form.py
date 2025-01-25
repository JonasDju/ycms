import logging

from ..models import Ward, Floor, Room, Bed
from .custom_model_form import CustomModelForm

logger = logging.getLogger(__name__)

class BedForm(CustomModelForm):
    """
    Form for creating beds
    """

    class Meta:
        """
        This class contains additional meta configuration of the form class, see the :class:`django.forms.ModelForm`
        for more information.
        """

        model = Bed
        fields = ["bed_type", "bed_blocking_type", "bed_blocking_reason"]

    def clean_bed_blocking_type(self):
        bed_blocking_type = self.cleaned_data.get("bed_blocking_type")
        if bed_blocking_type == "None":
            return None 
        return bed_blocking_type
