import datetime
import logging

from django import forms
from django.utils.translation import gettext_lazy as _

from ..models import BedAssignment
from ..models.timetravel_manager import current_or_travelled_time
from .custom_model_form import CustomModelForm

logger = logging.getLogger(__name__)


class IntakeBedAssignmentForm(CustomModelForm):
    """
    Form for creating intake bed assignments. Not used for assignment by station managers.
    """

    class Meta:
        """
        This class contains additional meta configuration of the form class, see the :class:`django.forms.ModelForm`
        for more information.
        """

        model = BedAssignment
        fields = ["admission_date", "discharge_date", "recommended_ward", "accompanied"]
        widgets = {
            "admission_date": forms.DateTimeInput(
                format=("%Y-%m-%dT%H:%M"), attrs={"type": "datetime-local"}
            ),
            "discharge_date": forms.DateTimeInput(
                format=("%Y-%m-%dT%H:%M"), attrs={"type": "datetime-local"}
            ),
        }

    def __init__(self, *args, **kwargs):
        r"""
        Initialize medical record form

        :param \*args: The supplied arguments
        :type \*args: list

        :param \**kwargs: The supplied keyword arguments
        :type \**kwargs: dict
        """
        super().__init__(*args, **kwargs)
        self.fields["admission_date"].initial = current_or_travelled_time()
        self.fields[
            "discharge_date"
        ].initial = current_or_travelled_time() + datetime.timedelta(days=7)

    def save(self, commit=True):
        """
        This method extends the default ``save()``-method of the base :class:`~django.forms.ModelForm`
        to create a new bed assignment.

        :param commit: Whether or not the changes should be written to the database
        :type commit: bool

        :return: The saved medical record
        :rtype: ~ycms.cms.models.medical_record.MedicalRecord
        """
        if hasattr(self.instance, "is_update") and self.instance.is_update:
            return super().save(commit)
        cleaned_data = self.cleaned_data
        new_record = BedAssignment.objects.create(
            creator=self.instance.creator,
            medical_record=self.instance.medical_record,
            admission_date=cleaned_data["admission_date"],
            discharge_date=cleaned_data["discharge_date"],
            recommended_ward=cleaned_data["recommended_ward"],
            accompanied=cleaned_data["accompanied"],
        )
        return new_record
