from django.forms import Form, FileField, FileInput
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator

class UploadCSVForm(Form):
    file = FileField(
        label=_("Import patient data"),
        validators=[FileExtensionValidator(allowed_extensions=["csv"])],
        widget=FileInput(attrs={'accept':'.csv'})
    )