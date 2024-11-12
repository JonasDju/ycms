from django.apps import apps
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from .abstract_base_model import AbstractBaseModel
from .floor import Floor
from .patient import Patient
from .timetravel_manager import current_or_travelled_time
from .user import User


class Ward(AbstractBaseModel):
    """
    Data model representing a Ward.
    """

    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=current_or_travelled_time, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)
    ward_number = models.CharField(
        unique=True,
        max_length=32,
        verbose_name=_("ward number"),
        help_text=_("Number of the ward"),
    )
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=32,
        verbose_name=_("ward name"),
        help_text=_("Name this ward is commonly referred to by"),
    )

    @cached_property
    def total_beds(self):
        """
        Helper property for accessing the wards bed count

        :return: number of beds in the ward
        :rtype: int
        """
        return sum(room.total_beds for room in self.rooms.all())

    @cached_property
    def available_beds(self):
        """
        Helper property for accessing the wards free bed count

        :return: number of free beds in the ward
        :rtype: int
        """
        return sum(room.available_beds for room in self.rooms.all())

    @cached_property
    def occupied_beds(self):
        """
        Helper property for accessing the wards occupied bed count

        :return: number of occupied beds in the ward
        :rtype: int
        """
        return self.total_beds - self.available_beds

    @cached_property
    def patients(self):
        """
        Helper property for accessing all patients currently stationed in the ward

        :return: patients in the ward
        :rtype: list [ ~ycms.cms.models.patient.Patient ]
        """
        BedAssignment = apps.get_model(app_label="cms", model_name="BedAssignment")

        patient_ids = BedAssignment.objects.filter(
            models.Q(bed__room__ward=self)
            & (
                models.Q(admission_date__lte=current_or_travelled_time())
                & (
                    models.Q(discharge_date__gt=current_or_travelled_time())
                    | models.Q(discharge_date__isnull=True)
                )
            )
        ).values_list("medical_record__patient", flat=True)
        patients = Patient.objects.filter(pk__in=patient_ids)
        return patients

    def __str__(self):
        """
        This overwrites the default Django :meth:`~django.db.models.Model.__str__` method which would return ``Ward object (id)``.
        It is used in the Django admin backend and as label for ModelChoiceFields.

        :return: A readable string representation of the ward
        :rtype: str
        """
        return f"{self.name} (ward {self.ward_number})"

    def get_repr(self):
        """
        This overwrites the default Django ``__repr__()`` method which would return ``<Ward: Ward object (id)>``.
        It is used for logging.

        :return: The canonical string representation of the ward
        :rtype: str
        """
        return f"<Ward (number: {self.ward_number})>"

    class Meta:
        verbose_name = _("ward")
        verbose_name_plural = _("wards")
