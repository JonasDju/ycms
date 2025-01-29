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
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        diagnosis_field = self.fields["diagnosis_code"]
        diagnosis_initial = None

        if self.instance.pk:
            self.fields["record_type"].widget = forms.HiddenInput()

            if self.instance.diagnosis_code:
                diagnosis_initial = (
                    self.instance.diagnosis_code.id,
                    f"{self.instance.diagnosis_code.code} --- {self.instance.diagnosis_code.description}",
                )
        else:
            choices = dict(record_types.CHOICES)
            del choices[record_types.INTAKE]
            self.fields["record_type"].choices = choices.items()

        # configure diagnosis select element based on permissions to change diagnosis code
        diagnosis_field.widget.attrs["class"] = "async_diagnosis_code"
        diagnosis_field.widget.attrs[
            "id"
        ] = f"search-{str(uuid.uuid4())[:6]}"

        if user and (user.is_superuser or user.job_type == "DOCTOR"):
            # user can edit the diagnosis field
            diagnosis_field.choices = [diagnosis_initial] if diagnosis_initial else [("", _("Search for diagnosis code"))]
            diagnosis_field.widget.attrs["disabled"] = False
        else:
            # user cannot edit the field
            diagnosis_field.choices = [diagnosis_initial] if diagnosis_initial else [("-", "-")]
            # don't set async_diagnosis_code class so tomselect will not be initialized
            diagnosis_field.widget.attrs["disabled"] = True
