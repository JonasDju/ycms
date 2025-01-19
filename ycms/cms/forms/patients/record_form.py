import logging
import uuid

from django import forms
from django.utils.translation import gettext_lazy as _

from ...constants import record_types
from ...models import MedicalRecord
from ..custom_model_form import CustomModelForm

logger = logging.getLogger(__name__)


class RecordForm(CustomModelForm):
    """
    Form for editing records.
    """

    class Meta:
        """
        This class contains additional meta configuration of the form class, see the :class:`django.forms.ModelForm`
        for more information.
        """

        model = MedicalRecord
        fields = ["record_type", "medical_specialization", "diagnosis_code", "note"]

    def __init__(self, *args, **kwargs):
        r"""
        Initialize medical record form

        :param \*args: The supplied arguments
        :type \*args: list

        :param \**kwargs: The supplied keyword arguments
        :type \**kwargs: dict
        """
        super().__init__(*args, **kwargs)

        self.fields["diagnosis_code"].choices = [("", _("Search for diagnosis code"))]
        self.fields["diagnosis_code"].widget.attrs["class"] = "async_diagnosis_code"
        self.fields["diagnosis_code"].widget.attrs[
            "id"
        ] = f"search-{str(uuid.uuid4())[:6]}"
        if self.instance.pk:
            if self.instance.diagnosis_code:
                initial = (
                    self.instance.diagnosis_code.id,
                    f"{self.instance.diagnosis_code.code} --- {self.instance.diagnosis_code.description}",
                )
                self.fields["diagnosis_code"].choices = [initial]

            self.fields["record_type"].widget = forms.HiddenInput()
        else:
            choices = dict(record_types.CHOICES)
            del choices[record_types.INTAKE]
            self.fields["record_type"].choices = choices.items()
