from django.forms import Form, FileField, FileInput, ChoiceField
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator

class UploadCSVForm(Form):
    CATEGORY_CHOICES = (
        ("1", _("Patient only")),
        ("2", _("Patient + medical record")),
        ("3", _("Patient + stay")),
        ("4", _("Patient + ward")),
        ("5", _("Patient + bed")),
    )

    file = FileField(
        label=_("Import patient data"),
        validators=[FileExtensionValidator(allowed_extensions=["csv"])],
        widget=FileInput(attrs={'accept':'.csv'})
    )
    selected_categories = ChoiceField(
        label=_("Choose categories to import"),
        choices=CATEGORY_CHOICES
    )