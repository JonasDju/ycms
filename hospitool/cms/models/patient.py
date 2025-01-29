from datetime import datetime

from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from ..constants import gender, insurance_types, record_types
from .abstract_base_model import AbstractBaseModel
from .timetravel_manager import current_or_travelled_time, TimetravelManager
from .user import User


class Patient(AbstractBaseModel):
    """
    Data model representing a Patient.
    """

    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=current_or_travelled_time, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)
    insurance_type = models.BooleanField(
        verbose_name=_("insurance type"),
        help_text=_("Whether the patient is privately insured or not"),
        choices=insurance_types.CHOICES,
        default=insurance_types.STATUTORY,
    )
    first_name = models.CharField(
        max_length=32,
        verbose_name=_("first name"),
        help_text=_("First name of the patient"),
    )
    last_name = models.CharField(
        max_length=64,
        verbose_name=_("last name"),
        help_text=_("Last name of the patient"),
    )
    gender = models.CharField(
        max_length=1,
        choices=gender.CHOICES,
        verbose_name=_("gender"),
        help_text=_("Gender of the patient"),
        default=None,
    )
    date_of_birth = models.DateField(
        verbose_name=_("date of birth"), help_text=_("Date of birth of the patient")
    )
    _first = models.CharField(max_length=32, blank=True)
    _last = models.CharField(max_length=64, blank=True)

    objects = TimetravelManager()

    @cached_property
    def age(self):
        """
        Helper property to get the patient's age in years

        :return: the patient's age in years
        :rtype: int
        """
        today = datetime.today().date()
        years_ago = today.year - self.date_of_birth.year
        if today.month < self.date_of_birth.month or (
            today.month == self.date_of_birth.month
            and today.day < self.date_of_birth.day
        ):
            return max(0, years_ago - 1)
        return max(0, years_ago)

    @cached_property
    def insurance_name(self):
        """
        Helper property to get the human-readable representation of the patient's
        insurance type
        """
        return dict(insurance_types.CHOICES)[self.insurance_type]

    @cached_property
    def short_info(self):
        """
        Helper property to get a short info string about the patient

        :return: the patient's info as a short string
        :rtype: str
        """
        age = _("age")
        insurance = _("insurance")
        return f"{self.first_name[0]}. {self.last_name} ({age}: {self.age}, {insurance}: {self.insurance_name})"

    @cached_property
    def current_stay(self):
        """
        Helper property for accessing the patient's current hospital stay

        :return: the current bed assignment
        :rtype: ~hospitool.cms.models.bed_assignment.BedAssignment
        """
        hospital_stay = self.medical_records.filter(
            models.Q(record_type=record_types.INTAKE)
            & models.Q(bed_assignment__admission_date__lte=current_or_travelled_time())
            & (
                models.Q(bed_assignment__discharge_date__isnull=True)
                | models.Q(
                    bed_assignment__discharge_date__gt=current_or_travelled_time()
                )
            )
        ).first()
        return hospital_stay.bed_assignment.get() if hospital_stay else None

    @cached_property
    def current_bed(self):
        """
        Helper property for accessing the patient's current bed

        :return: the current bed
        :rtype: ~hospitool.cms.models.bed.Bed
        """
        return self.current_stay.bed if self.current_stay else None

    @cached_property
    def current_diagnose(self):
        """
        Helper property for accessing the patient's current bed
        :return: the current diagnose code
        :rtype: str
        """
        return self.current_stay.medical_record.diagnosis_code if self.current_stay else None

    @cached_property
    def current_room(self):
        """
        Helper property for accessing the patient's current room

        :return: the current room
        :rtype: ~hospitool.cms.models.room.Room
        """
        return self.current_bed.room if self.current_bed else None

    @cached_property
    def current_room_short(self):
        """
        Helper property for accessing the patient's current room
        :return: the current room_number in short
        :rtype: str
        """
        return self.current_bed.room.room_number if self.current_bed else None

    @cached_property
    def current_ward(self):
        """
        Helper property for accessing the patient's current ward

        :return: the current ward
        :rtype: ~hospitool.cms.models.ward.Ward
        """
        return self.current_room.ward if self.current_room else None

    @staticmethod
    def _get_date_status(date_to_check):
        """
        Helper function to get the date status of a given date

        :param date_to_check: the date to check
        :type date_to_check: datetime.date
        :return: the date status
        :rtype: str
        """
        if not date_to_check:
            return None

        today = _("today")
        days_ago = _("{} days ago")
        day_ago = _("{} day ago")
        in_days = _("in {} days")
        in_day = _("in {} day")

        if not (
            days_since := (
                current_or_travelled_time().date() - date_to_check.date()
            ).days
        ):
            return f'{date_to_check.strftime("%b. %d, %Y")} ({today})'

        if days_since > 0:
            return f"{date_to_check.strftime('%b. %d, %Y')} ({ day_ago.format(days_since) if days_since == 1 else days_ago.format(days_since)})"

        days_until = abs(days_since)
        return f"{date_to_check.strftime('%b. %d, %Y')} ({in_day.format(days_until) if days_until == 1 else in_days.format(days_until)})"

    @cached_property
    def current_admission_date(self):
        """
        Helper property for accessing the patient's current admission date

        :return: the current admission date
        :rtype: str
        """
        if not self.current_stay:
            return None
        return self._get_date_status(self.current_stay.admission_date)

    @cached_property
    def current_discharge_date(self):
        """
        Helper property for accessing the patient's current discharge date

        :return: the current discharge date
        :rtype: str
        """
        if not self.current_stay:
            return None
        return self._get_date_status(self.current_stay.discharge_date)

    def __str__(self):
        """
        This overwrites the default Django :meth:`~django.db.models.Model.__str__` method which would return ``Patient object (id)``.
        It is used in the Django admin backend and as label for ModelChoiceFields.

        :return: A readable string representation of the patient
        :rtype: str
        """
        return f"{self.last_name}, {self.first_name} (patient {self.id})"

    def get_repr(self):
        """
        This overwrites the default Django ``__repr__()`` method which would return ``<Patient: Patient object (id)>``.
        It is used for logging.

        :return: The canonical string representation of the patient
        :rtype: str
        """
        return f"<Patient (id: {self.id})>"

    class Meta:
        verbose_name = _("patient")
        verbose_name_plural = _("patients")
