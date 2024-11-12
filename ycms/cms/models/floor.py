from django.apps import apps
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from ..constants import insurance_types
from .abstract_base_model import AbstractBaseModel
from .timetravel_manager import current_or_travelled_time


class Floor(AbstractBaseModel):
    """
    Data model representing a Floor.
    """

    created_at = models.DateTimeField(default=current_or_travelled_time, null=False)
    updated_at = models.DateTimeField(auto_now=True, null=False)
    order = models.IntegerField(
        verbose_name=_("floor order"), help_text=_("Order of the floor")
    )
    full_name = models.CharField(
        null=True,
        max_length=30,
        verbose_name=_("floor name"),
        help_text=_("Name of the floor"),
    )
    short_name = models.CharField(
        null=True,
        max_length=10,
        verbose_name=_("floor code"),
        help_text=_("Shortname of the floor"),
    )

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
