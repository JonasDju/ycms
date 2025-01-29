import logging
from datetime import date

from django import forms
from django.utils.translation import gettext_lazy as _

from ..constants import insurance_types
from ..models import Patient
from .custom_model_form import CustomModelForm

logger = logging.getLogger(__name__)


class UnknownPatientForm(CustomModelForm):
    """
    Form for creating placeholder patients
    """

    prefix = "unknown"

    approximate_age = forms.IntegerField(
        label=_("Approximate age"),
        help_text=_("Best guess for the patient's approximate age"),
        min_value=0,
        max_value=100,
        step_size=5,
        widget=forms.NumberInput(attrs={"type": "range"}),
    )

    class Meta:
        """
        This class contains additional meta configuration of the form class, see the :class:`django.forms.ModelForm`
        for more information.
        """

        model = Patient
        fields = ["gender"]
        widgets = {"gender": forms.RadioSelect()}

    def save(self, commit=True):
        """
        This method extends the default ``save()``-method of the base :class:`~django.forms.ModelForm`
        to create a new bed assignment.

        :param commit: Whether or not the changes should be written to the database
        :type commit: bool

        :return: The saved bed assignment
        :rtype: ~hospitool.cms.models.bed_assignment.BedAssignment
        """
        cleaned_data = self.cleaned_data
        patient = Patient.objects.create(
            creator=self.instance.creator,
            first_name="Unbekannt",
            last_name="Unbekannt",
            gender=cleaned_data["gender"],
            insurance_type=insurance_types.STATUTORY,
            date_of_birth=date(
                date.today().year - cleaned_data["approximate_age"], 1, 1
            ),
        )
        return patient
