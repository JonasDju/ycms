import logging

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .custom_model_form import CustomModelForm
from ..models import MedicalSpecialization

logger = logging.getLogger(__name__)

class MedicalSpecializationForm(CustomModelForm):
    """
    From for creating/updating medical specializations
    """

    class Meta:
        """
        This class contains additional meta configuration of the form class, see the :class:`django.forms.ModelForm`
        for more information.
        """
        
        model = MedicalSpecialization
        fields = ["name", "abbreviation"]

    def clean(self):
        """
        This method extends the default ``clean()``-method of the base :class:`~django.forms.ModelForm`
        to check if the specialization conflicts with an existing one.

        :return: The cleaned data
        """
        cleaned_data = super().clean()
        abbr = cleaned_data.get("abbreviation")

        if MedicalSpecialization.objects.filter(abbreviation__iexact=abbr).exists():
            raise ValidationError(
                _("The abbreviation {} conflicts with an existing one.".format(abbr))
            )
        
        return cleaned_data