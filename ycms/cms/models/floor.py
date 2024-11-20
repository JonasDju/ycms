from django.apps import apps
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from . import Patient
from .abstract_base_model import AbstractBaseModel
from .timetravel_manager import current_or_travelled_time


class Floor(AbstractBaseModel):
    """
    Data model representing a Floor.
    """

    created_at = models.DateTimeField(default=current_or_travelled_time, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)
    # successor = models.ForeignKey('self') # TODO(jan) use this instead of order -> unique, make sure deletion is handled well
    # predecessor = models.ForeignKey('self') # TODO(jan) use this instead of order -> unique, make sure deletion is handled well
    order = models.IntegerField(  # TODO(jan) unique remove later
        verbose_name=_("floor order"), help_text=_("Order of the floor")
    )
    name = models.CharField(
        null=True,
        max_length=30,
        verbose_name=_("floor name"),
        help_text=_("Name of the floor"),
    )
    code = models.CharField(
        null=True,
        max_length=10,
        verbose_name=_("floor code"),
        help_text=_("Shortname of the floor"),
    )

    @cached_property
    def total_beds(self):
        """
        Helper property for accessing the floor bed count

        :return: number of beds in the ward
        :rtype: int
        """
        return sum(ward.total_beds for ward in self.wards.all())

    @cached_property
    def available_beds(self):
        """
        Helper property for accessing the floor free bed count

        :return: number of free beds in the ward
        :rtype: int
        """
        return sum(ward.available_beds for ward in self.wards.all())

    @cached_property
    def occupied_beds(self):
        """
        Helper property for accessing the floor occupied bed count

        :return: number of occupied beds in the ward
        :rtype: int
        """
        return self.total_beds - self.available_beds

    @cached_property
    def patients(self):
        """
        Helper property for accessing all patients currently stationed on the floor

        :return: patients in the ward
        :rtype: list [ ~ycms.cms.models.patient.Patient ]
        """
        BedAssignment = apps.get_model(app_label="cms", model_name="BedAssignment")
        patient_ids = []

        for ward in self.wards.all():
            patient_ids += BedAssignment.objects.filter(
                models.Q(bed__room__ward=ward)
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
        This overwrites the default Django :meth:`~django.db.models.Model.__str__` method which would return ``Room object (id)``.
        It is used in the Django admin backend and as label for ModelChoiceFields.

        :return: A readable string representation of the room
        :rtype: str
        """
        return f"Floor {self.code} '{self.name}'"

    def get_repr(self):
        """
        This overwrites the default Django ``__repr__()`` method which would return ``<Room: Room object (id)>``.
        It is used for logging.

        :return: The canonical string representation of the room
        :rtype: str
        """
        return f"<Floor (code: {self.code}, name: {self.name})>"

    class Meta:
        verbose_name = _("floor")
        verbose_name_plural = _("floors")
