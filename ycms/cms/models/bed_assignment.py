from django.db import models
from django.utils.translation import gettext_lazy as _

from .abstract_base_model import AbstractBaseModel
from .bed import Bed
from .medical_record import MedicalRecord
from .timetravel_manager import current_or_travelled_time, TimetravelManager
from .user import User
from .ward import Ward


class BedAssignment(AbstractBaseModel):
    """
    Data model representing a BedAssignment.
    """

    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=current_or_travelled_time, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)
    admission_date = models.DateTimeField(
        blank=True,
        verbose_name=_("admission date"),
        help_text=_("date the hostpital stay begins"),
    )
    discharge_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("discharge date"),
        help_text=_("date the hospital stay ends"),
    )
    accompanied = models.BooleanField(
        blank=True,
        default=False,
        verbose_name=_("accompanied"),
        help_text=_("Whether the patient is accompanied by a chaperone"),
    )
    medical_record = models.ForeignKey(
        MedicalRecord,
        related_name="bed_assignment",
        on_delete=models.CASCADE,
        verbose_name=_("medical record"),
        help_text=_("The medical record associated with this bed assignment"),
    )
    recommended_ward = models.ForeignKey(
        Ward,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("recommended ward"),
        help_text=_("Recommendation for stay at this ward"),
    )
    bed = models.ForeignKey(
        Bed,
        related_name=("assignments"),
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_("bed"),
        help_text=_("The bed assigned to the patient"),
    )

    objects = TimetravelManager()

    def __str__(self):
        """
        This overwrites the default Django :meth:`~django.db.models.Model.__str__` method which would return ``BedAssignment object (id)``.
        It is used in the Django admin backend and as label for ModelChoiceFields.

        :return: A readable string representation of the bed assignment
        :rtype: str
        """
        return f"BedAssignment {self.id} (Patient {self.medical_record.patient}, Bed {self.bed})"

    def get_repr(self):
        """
        This overwrites the default Django ``__repr__()`` method which would return ``<BedAssignment: BedAssignment object (id)>``.
        It is used for logging.

        :return: The canonical string representation of the bed assignment
        :rtype: str
        """
        return f"<BedAssignment (id: {self.id})>"

    class Meta:
        verbose_name = _("bed assignment")
        verbose_name_plural = _("bed assignments")
