import logging

from django import forms

from ..models import Patient
from .custom_model_form import CustomModelForm

logger = logging.getLogger(__name__)


class PatientForm(CustomModelForm):
    """
    Form for creating patients
    """

    class Meta:
        """
        This class contains additional meta configuration of the form class, see the :class:`django.forms.ModelForm`
        for more information.
        """

        model = Patient
        fields = [
            "first_name",
            "last_name",
            "gender",
            "date_of_birth",
            "insurance_type",
        ]
        widgets = {
            "date_of_birth": forms.NumberInput(attrs={"type": "date"}),
            "gender": forms.RadioSelect(),
            "insurance_type": forms.RadioSelect(),
        }
