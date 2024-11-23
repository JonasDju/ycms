from django.forms import Form, FileField
from django.utils.translation import gettext_lazy as _

class UploadCSVForm(Form):
    file = FileField(label=_("Select CSV file"))