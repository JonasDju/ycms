from django.db import models
from django.utils.translation import gettext_lazy as _

from .abstract_base_model import AbstractBaseModel


class ICD10Entry(AbstractBaseModel):
    """
    Data model representing an ICD-10 Entry.
    """

    code = models.CharField(
        unique=True,
        max_length=21,
        verbose_name=_("code"),
        help_text=_("ICD-10-GM classification code"),
    )
    description = models.CharField(
        max_length=256,
        verbose_name=_("description"),
        help_text=_("ICD-10-GM classification description"),
    )

    def __str__(self):
        """
        This overwrites the default Django :meth:`~django.db.models.Model.__str__` method which would return ``ICD10Entry object (id)``.
        It is used in the Django admin backend and as label for ModelChoiceFields.

        :return: A readable string representation of the ICD-10-GM entry
        :rtype: str
        """
        return f"ICD-10-GM Entry {self.code}"

    def get_repr(self):
        """
        This overwrites the default Django ``__repr__()`` method which would return ``<ICD10Entry: ICD10Entry object (id)>``.
        It is used for logging.

        :return: The canonical string representation of the ICD-10-GM entry
        :rtype: str
        """
        return f"<ICD-10-GM Entry {self.code}>"

    class Meta:
        verbose_name = _("ICD-10 entry")
        verbose_name_plural = _("ICD-10 entries")
