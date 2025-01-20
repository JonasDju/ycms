import logging

from ..models import Ward, Floor, Room, Bed
from .custom_model_form import CustomModelForm

logger = logging.getLogger(__name__)


class RoomForm(CustomModelForm):
    """
    Form for creating rooms
    """

    class Meta:
        """
        This class contains additional meta configuration of the form class, see the :class:`django.forms.ModelForm`
        for more information.
        """

        model = Room
        fields = ["room_number"]
