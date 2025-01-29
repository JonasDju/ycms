import logging

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import TemplateView

from ...decorators import permission_required
from ...models import Bed, BedAssignment, Ward
from ...models.timetravel_manager import current_or_travelled_time

logger = logging.getLogger(__name__)


@method_decorator(permission_required("cms.change_patient"), name="dispatch")
class AssignPatientView(TemplateView):
    """
    View allowing to assign the bed assignment visually
    """

    model = BedAssignment
    template_name = "bed_assignment/assign_bed_assignment.html"
    context_object_name = "bed_assignment"

    def get_context_data(self, **kwargs):
        ward_id = self.kwargs["ward_id"]
        assignment_id = self.kwargs["assignment_id"]

        ward = Ward.objects.get(id=ward_id)
        rooms = ward.rooms.all()
        wards = Ward.objects.all()
        bed_assignment = get_object_or_404(BedAssignment, id=assignment_id)

        return {
            "bed_assignment": bed_assignment,
            "rooms": rooms,
            "corridor_index": len(rooms) // 2,
            "ward": ward,
            "wards": wards,
            **super().get_context_data(**kwargs),
        }

    def post(self, request, *args, **kwargs):
        """
        This function assigns a patient to a room
        """
        assignment_id = kwargs["assignment_id"]
        bed_assignment = get_object_or_404(BedAssignment, pk=assignment_id)

        bed_id = request.POST.get("bed_id")
        try:
            bed_assignment.bed = Bed.objects.get(pk=bed_id)
            message = _('Successfully assigned "{}, {}" to bed {} in room {}.').format(
                bed_assignment.medical_record.patient.last_name,
                bed_assignment.medical_record.patient.first_name,
                bed_assignment.bed.id,
                bed_assignment.bed.room.room_number,
            )
        except Bed.DoesNotExist:
            bed_assignment.bed = None
            message = _('Successfully unassigned "{}, {}".').format(
                bed_assignment.medical_record.patient.last_name,
                bed_assignment.medical_record.patient.first_name,
            )

        if new_ward_id := request.POST.get("new_ward"):
            bed_assignment.recommended_ward = get_object_or_404(Ward, pk=new_ward_id)
            message = _('Successfully moved "{}, {}" to {}.').format(
                bed_assignment.medical_record.patient.last_name,
                bed_assignment.medical_record.patient.first_name,
                Ward.objects.get(pk=new_ward_id).name,
            )

        bed_assignment.updated_at = current_or_travelled_time()
        bed_assignment.save()
        messages.success(request, message)

        drawer = (
            bed_assignment.bed.room.room_number
            if bed_assignment.bed
            else "unassigned"
            if not new_ward_id
            else "none"
        )
        next_ = request.POST["next"]
        if "?" in next_:
            next_ = next_.split("?")[0]

        return HttpResponseRedirect(f"{next_}?drawer=drawer-right-{drawer}")
