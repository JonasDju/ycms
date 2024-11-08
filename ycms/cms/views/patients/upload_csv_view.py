import logging

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render, reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import TemplateView

from ...decorators import permission_required
from ...forms import (
    IntakeBedAssignmentForm,
    IntakeRecordForm,
    PatientForm,
    UnknownPatientForm,
)
from ...models import Patient
from ...models.timetravel_manager import current_or_travelled_time

from pathlib import Path
from ...import_data import import_data

logger = logging.getLogger(__name__)


@method_decorator(permission_required("cms.add_patient"), name="dispatch")
class UploadCsvView(TemplateView):
    """
    View to import patient data from an uploaded .csv file into database
    """

    # TODO new template necessary
    template_name = "patients/patient_intake_form.html"

    # upload patients with a csv file
    def uploaded_patients(request):
        # write chunks to a temporary file
        with open("./bed_manager/temp/temp.csv", "wb") as f:
            for chunk in request.FILES["filepath"].chunks():
                f.write(chunk)
        # read temporary file and use it for import
        import_data("./bed_manager/temp/temp.csv", sep=",")
        # delete temporary file
        os.remove("./bed_manager/temp/temp.csv")
        return redirect("bed_manager:patient_overview")
