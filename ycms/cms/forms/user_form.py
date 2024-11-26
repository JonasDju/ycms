from ..models import User
from .custom_model_form import CustomModelForm


class UserForm(CustomModelForm):
    """
    Form for editing users
    """

    class Meta:
        """
        This class contains additional meta configuration of the form class, see the :class:`django.forms.ModelForm`
        for more information.
        """

        model = User
        fields = ["first_name", "last_name", "assigned_ward", "ward_as_timeline"]
