from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from ..constants import record_types
from .abstract_base_model import AbstractBaseModel
from .icd10_entry import ICD10Entry
from .medical_specialization import MedicalSpecialization
from .patient import Patient
from .timetravel_manager import current_or_travelled_time, TimetravelManager
from .user import User


class MedicalRecord(AbstractBaseModel):
    """
    Data model representing a MedicalRecord.
    """

    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=current_or_travelled_time, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)
    patient = models.ForeignKey(
        Patient,
        related_name="medical_records",
        on_delete=models.CASCADE,
        verbose_name=_("patient"),
        help_text=_("The patient associated with this medical record"),
    )
    diagnosis_code = models.ForeignKey(
        ICD10Entry,
        on_delete=models.PROTECT,
        verbose_name=_("diagnosis code"),
        help_text=_("Diagnosis code according to ICD-10"),
        blank=True,
        null=True,
    )
    medical_specialization = models.ForeignKey(
        MedicalSpecialization,
        on_delete=models.PROTECT,
        verbose_name=_("medical specialization"),
        help_text=_("Medical specialization of the patient's treatment."),
        blank=True,
        null=True,
    )
    record_type = models.CharField(
        max_length=32,
        choices=record_types.CHOICES,
        verbose_name=_("record type"),
        help_text=_("type of this record"),
    )
    note = models.TextField(
        blank=True,
        verbose_name=_("note"),
        help_text=_("Additional notes for this medical record"),
    )

    objects = TimetravelManager()

    @cached_property
    def record_name(self):
        """
        Helper property to get the human-readable representation of the record's type
        """
        return dict(record_types.CHOICES)[self.record_type]

    def __str__(self):
        """
        This overwrites the default Django :meth:`~django.db.models.Model.__str__` method which would return ``MedicalRecord object (id)``.
        It is used in the Django admin backend and as label for ModelChoiceFields.

        :return: A readable string representation of the medical record
        :rtype: str
        """
        return f"MedicalRecord {self.id} for {self.patient})"

    def get_repr(self):
        """
        This overwrites the default Django ``__repr__()`` method which would return ``<MedicalRecord: MedicalRecord object (id)>``.
        It is used for logging.

        :return: The canonical string representation of the medical record
        :rtype: str
        """
        return f"<MedicalRecord for {self.patient} (id: {self.id})>"

    class Meta:
        verbose_name = _("medical record")
        verbose_name_plural = _("medical records")
        get_latest_by = "-created_at"
