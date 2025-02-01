import logging

from django import forms

from ..constants import days_of_week
from ..models import Ward, Floor
from .custom_model_form import CustomModelForm

logger = logging.getLogger(__name__)

class WeekdaySelectField(forms.MultipleChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs["choices"] = [(0b1 << day, name) for day, name in enumerate(days_of_week.WEEKDAYS_SHORT)]
        super().__init__(*args, **kwargs)

    def prepare_value(self, value):
        """ Convert binary-encoded int backing field to selection of weekdays. """
        if isinstance(value, int):
            return [day for day, name in enumerate(days_of_week.WEEKDAYS_LONG) if value & day]
        return value
    
    def to_python(self, value):
        """ Convert list of selected weekdays to binary-encoded int used as backing. """
        if not value:
            return 0
        return (sum(int(v) for v in value))
    
    def validate(self, value):
        return isinstance(value, int)

class WardForm(CustomModelForm):
    """
    Form for creating wards
    """

    class Meta:
        """
        This class contains additional meta configuration of the form class, see the :class:`django.forms.ModelForm`
        for more information.
        """

        model = Ward
        fields = ["name", "nickname", "floor", "allowed_discharge_days"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["floor"].queryset = Floor.objects.order_by("-order")
        self.fields["floor"].label_from_instance = lambda obj: obj.name

        # update weekday field to expose a selection (rather than default integer text-field)
        backing_field = self.instance._meta.get_field("allowed_discharge_days")

        self.fields["allowed_discharge_days"] = WeekdaySelectField(
            help_text=backing_field.help_text,
            label=self.fields["allowed_discharge_days"].label
        )

        # set initial value for weekday field based on backing value (int)
        if self.instance:
            self.initial["allowed_discharge_days"] = self.instance.allowed_discharge_days_binary