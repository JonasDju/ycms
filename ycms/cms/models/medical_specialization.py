from django.db import models
from django.utils.translation import gettext_lazy as _

from .abstract_base_model import AbstractBaseModel


class MedicalSpecialization(AbstractBaseModel):
    """
    Data model representing a medical specialization.
    """

    name = models.CharField(
        max_length=256,
        verbose_name=_("specialization name"),
        help_text=_("Name of this medical specialization."),
    )
    abbreviation = models.CharField(
        max_length=8,
        verbose_name=_("abbreviation"),
        help_text=_("Abbreviation of this medical specialization."),
    )

    def __str__(self):
        """
        This overwrites the default Django :meth:`~django.db.models.Model.__str__` method which would return ``MedicalSpecialization object (id)``.
        It is used in the Django admin backend and as label for ModelChoiceFields.

        :return: A readable string representation of the medical specialization entry
        :rtype: str
        """
        if self.abbreviation != None and self.abbreviation != "":
            return f"{self.name} ({self.abbreviation})"
        else:
            return f"{self.name}"

    def get_repr(self):
        """
        This overwrites the default Django ``__repr__()`` method which would return ``<MedicalSpecialization: MedicalSpecialization object (id)>``.
        It is used for logging.

        :return: The canonical string representation of the medical specialization entry
        :rtype: str
        """
        if self.abbreviation != None and self.abbreviation != "":
            return f"<Medical specialization {self.name} ({self.abbreviation})>"
        else:
            return f"<Medical specialization {self.name}>"

    class Meta:
        verbose_name = _("medical specialization")
        verbose_name_plural = _("medical specializations")
