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
        validators=[FileExtensionValidator(allowed_extensions=["csv"])],
        widget=FileInput(
            attrs={
                'accept':'.csv',
                #'class':'px-2 text-white bg-blue-500 hover:bg-blue-700 mt-2 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:focus:ring-blue-700 rounded px-5 py-2.5 text-center w-full lg:w-auto',
                'class':'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-100 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400'
            }
        )
    )
    selected_categories = ChoiceField(
        label=_("Choose categories to import"),
        choices=CATEGORY_CHOICES
    )