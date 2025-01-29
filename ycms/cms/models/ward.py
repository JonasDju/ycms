from django.apps import apps
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from ..constants import days_of_week
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
    floor = models.ForeignKey(Floor, on_delete=models.CASCADE, help_text=_("Floor this ward is located on"))
    name = models.CharField(
        max_length=32,
        verbose_name=_("ward name"),
        help_text=_("Name this ward is commonly referred to by"),
    )
    nickname = models.CharField(
        max_length=32,
        verbose_name=_("ward nickname"),
        help_text=_("Nickname of this ward"),
        blank=True,
        default="",
    )
    allowed_discharge_days = models.SmallIntegerField(
        default=127,  # binary mask, zero-indexed starting at Monday
        verbose_name=_("allowed discharge days"),
        help_text=_("Days of the week where discharges are allowed in this ward"),
        validators=[
            MinValueValidator(0),  # 0b0000000
            MaxValueValidator(127),  # 0b1111111
        ],
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
        return sum(room.occupied_beds for room in self.rooms.all())
    
    @cached_property
    def total_blocked_beds(self):
        """
        Helper property for accessing the wards occupied bed count

        :return: number of blocked beds in the ward
        :rtype: int
        """
        return sum(room.total_blocked_beds for room in self.rooms.all())

    @cached_property
    def occupation_rate(self):
        """
        Helper property for accessing the wards occupation rate

        :return: percentage rate of occupied beds rounded to two digits
        :rtype: float
        """
        if self.total_beds == 0:
            return 100.0
        return round(self.occupied_beds / self.total_beds * 100, 2)

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

    @cached_property
    def unassigned_patients(self):
        """
        Helper property for accessing all patients currently stationed in the ward

        :return: patients in the ward
        :rtype: list [ ~ycms.cms.models.patient.Patient ]
        """
        BedAssignment = apps.get_model(app_label="cms", model_name="BedAssignment")

        patient_ids = BedAssignment.objects.filter(
            models.Q(admission_date__lte=current_or_travelled_time())
            & models.Q(bed__isnull=True)
            & (
                models.Q(discharge_date__gt=current_or_travelled_time())
                | models.Q(discharge_date__isnull=True)
            )
            & (
                models.Q(recommended_ward=self)
                # | models.Q(recommended_ward__isnull=True) uncomment if you want to include patients that do not
                # have a recommended ward
            )
        ).values_list("medical_record__patient", flat=True)

        patients = Patient.objects.filter(pk__in=patient_ids)
        return patients

    @cached_property
    def patient_genders(self):
        """
        Helper property for accessing a dictionary representing the gener of patients currently stationed in the ward

        :return: gender of patients in the ward
        :rtype: dict [ str, str ]
        """
        gender_dict = {}
        for patient in self.patients:
            if patient.gender not in gender_dict:
                gender_dict[patient.gender] = 0
            gender_dict[patient.gender] += 1
        # sort the dictionary to make sure the order is the same always
        return {
            t[0]: t[1]
            for t in sorted(gender_dict.items(), key=lambda x: x[0], reverse=True)
        }
    
    @cached_property
    def allowed_discharge_days_binary(self):
        """
        Helper property for accessing a list of the configured days where discharged are allowed as binary values.
        The values are bitshifted by their position in the week, i.e. Mo = 0b1, Tue = 0b01, ..., Sun = 0b1000000.

        :return: list of allowed discharge days in the ward 
        :rtype: list [ int ]
        """
        if self.allowed_discharge_days:
            return [
                (0b1 << day) for day, _ in enumerate(days_of_week.WEEKDAYS_LONG) if self.allowed_discharge_days & (0b1 << day)
            ]
        else:
            return []

    def __str__(self):
        """
        This overwrites the default Django :meth:`~django.db.models.Model.__str__` method which would return ``Ward object (id)``.
        It is used in the Django admin backend and as label for ModelChoiceFields.

        :return: A readable string representation of the ward
        :rtype: str
        """

        if self.nickname != None and self.nickname != "":
            return f"{self.nickname}"
        else:
            return f"{self.name}"

    def get_repr(self):
        """
        This overwrites the default Django ``__repr__()`` method which would return ``<Ward: Ward object (id)>``.
        It is used for logging.

        :return: The canonical string representation of the ward
        :rtype: str
        """
        return f"<Ward (name: {self.name})>"

    class Meta:
        verbose_name = _("ward")
        verbose_name_plural = _("wards")
        unique_together = ('floor', 'name')
