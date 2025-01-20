from django.apps import apps
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from ..constants import insurance_types
from .abstract_base_model import AbstractBaseModel
from .patient import Patient
from .timetravel_manager import current_or_travelled_time
from .user import User
from .ward import Ward


class Room(AbstractBaseModel):
    """
    Data model representing a Room.
    """

    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=current_or_travelled_time, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)
    room_number = models.CharField(
        max_length=32,
        verbose_name=_("room number"),
        help_text=_("number of this room within its ward"),
    )
    ward = models.ForeignKey(
        Ward,
        related_name="rooms",
        on_delete=models.CASCADE,
        verbose_name=_("ward"),
        help_text=_("The ward this room belongs to"),
    )

    @cached_property
    def total_beds(self):
        """
        Helper property for accessing the rooms bed count

        :return: number of beds in the room
        :rtype: int
        """
        return self.beds.count()

    @cached_property
    def available_beds(self):
        """
        Helper property for accessing the rooms free bed count

        :return: number of free beds in the room
        :rtype: int
        """
        accompanied_count = sum(
            1 for patient in self.patients() if patient.current_stay.accompanied
        )
        return max(
            0, sum(1 for bed in self.beds.all() if bed.is_available) - accompanied_count
        )

    @cached_property
    def occupied_beds(self):
        """
        Helper property for accessing the rooms occupied bed count

        :return: number of occupied beds in the room
        :rtype: int
        """
        #return self.total_beds - self.available_beds
        return max(
            0, sum(1 for bed in self.beds.all() if bed.is_available)
        )
    
    @cached_property
    def total_blocked_beds(self):
        """
        Helper property for accessing the rooms blocked bed count

        :return: number of blocked beds in the room
        :rtype: int
        """
        return self.total_beds - self.available_beds - self.occupied_beds 


    def patients(self):
        """
        Helper property for accessing all patients currently stationed in the room

        :return: patients in the room
        :rtype: list [ ~ycms.cms.models.patient.Patient ]
        """
        BedAssignment = apps.get_model(app_label="cms", model_name="BedAssignment")

        patient_ids = BedAssignment.objects.filter(
            models.Q(bed__room=self)
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

    @cached_property
    def is_private(self):
        """
        Helper property for determining if the room should be considered private

        :return: whether this is a private room
        :rtype: boolean
        """
        return self.patients.filter(insurance_type=insurance_types.PRIVATE).exists()

    @cached_property
    def genders(self):
        """
        Helper property for accessing all genders of patients currently stationed in the room

        :return: genders of patients in the room
        :rtype: set
        """
        return set(patient.gender for patient in self.patients())

    @cached_property
    def insurance_types(self):
        """
        Helper property for accessing all insurance_types of patients currently stationed in the room

        :return: insurance_types of patients in the room
        :rtype: set
        """
        return set(patient.insurance_type for patient in self.patients())

    @cached_property
    def patient_ages(self):
        """
        Helper property for accessing ages of patients currently stationed in the room

        :return: ages of patients in the room
        :rtype: list
        """
        return [patient.age for patient in self.patients()] if self.patients() else [0]

    @cached_property
    def minus_max_age(self):
        """
        Helper property for accessing minus maximum age of patients currently stationed in the room

        :return: maximum age of patients in the room
        :rtype: int
        """
        return -max(self.patient_ages)

    @cached_property
    def age_difference_between_patients(self):
        """
        Helper property for accessing age difference between patients currently stationed in the room

        :return: age difference between patients in the room
        :rtype: int
        """
        return max(self.patient_ages) - min(self.patient_ages)

    @cached_property
    def assignable_beds(self):
        """
        Helper property for accessing the free bed

        :return: free beds in the room
        :rtype: list
        """
        return [bed for bed in self.beds.all() if bed.is_available]
    
    @cached_property
    def blocked_beds(self):
        """
        Helper property for accessing the free bed

        :return: free beds in the room
        :rtype: list
        """
        return [bed for bed in self.beds.all() if bed.is_blocked]

    def __str__(self):
        """
        This overwrites the default Django :meth:`~django.db.models.Model.__str__` method which would return ``Room object (id)``.
        It is used in the Django admin backend and as label for ModelChoiceFields.

        :return: A readable string representation of the room
        :rtype: str
        """
        return f"Room {self.room_number} in Ward {self.ward.nickname}"

    def get_repr(self):
        """
        This overwrites the default Django ``__repr__()`` method which would return ``<Room: Room object (id)>``.
        It is used for logging.

        :return: The canonical string representation of the room
        :rtype: str
        """
        return f"<Room (number: {self.room_number}, ward: {self.ward.nickname})>"

    class Meta:
        verbose_name = _("room")
        verbose_name_plural = _("rooms")
