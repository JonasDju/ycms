import json
import logging
from io import StringIO

from django.contrib import messages
from django.core.management import call_command
from django.db.models import Q
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
from django.core.cache import cache

from ...decorators import permission_required
from ...models import BedAssignment, Room, Ward
from ...models.timetravel_manager import current_or_travelled_time

logger = logging.getLogger(__name__)


@method_decorator(permission_required("cms.change_patient"), name="dispatch")
class TimelineView(TemplateView):
    """
    View to see a ward as a timeline
    """

    template_name = "timeline/timeline.html"

    # Intercept the GET request for the suggest path to execute the algorithm.
    # If the algorithm fails, redirect to normal timeline view.
    # If it succeeds, save the result in kwargs and proceed as normal.
    def dispatch(self, request, *args, **kwargs):
        if request.method == "GET" and "/suggest/" in request.path:

            # Redirect to return in case of errors
            error_redirect = redirect("cms:protected:timeline", pk=kwargs.get("pk"))

            # Check PRA installation / gurobi license status before executing the algorithm
            pra_algorithm_installed = cache.get("pra_algorithm_installed")
            gurobi_license = cache.get("gurobi_license")

            if not pra_algorithm_installed:
                messages.error(self.request, _("The PRA algorithm is not installed."))
                return error_redirect
            if gurobi_license == "missing":
                messages.error(self.request, _("The Gurobi license is missing. Please install it and try again."))
                return error_redirect
            if gurobi_license == "invalid":
                messages.error(self.request, _("The Gurobi license is invalid. Please update it and try again."))
                return error_redirect

            # PRA installed and gurobi license valid
            pk = kwargs.get("pk")
            out = StringIO()
            call_command("call_solver_api", pk, stdout=out)

            if not out.getvalue():
                messages.error(self.request, _("Algorithm failed to generate assignment."))
                return error_redirect

            kwargs["algorithm_result"] = json.loads(out.getvalue())

        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        """
        This function returns a list of all bed future or current bed assignments
        to the ward, formatted so that vis-timeline.js can visualize them

        :param kwargs: The supplied keyword arguments
        :type kwargs: dict

        :return: Response for filtered offers
        :rtype: ~django.template.response.TemplateResponse
        """
        pk = kwargs.get("pk")
        ward = Ward.objects.get(id=pk)
        wards = Ward.objects.all()

        suggestions = {}
        if "/suggest/" in self.request.path:
            suggestions = kwargs.get("algorithm_result")

        return {
            "ward": ward,
            "wards": wards,
            "selected_ward_id": pk,
            "timeline_data": self._get_timeline_data(ward, suggestions),
            "suggestions": json.dumps(suggestions),
            **super().get_context_data(**kwargs),
        }

    @staticmethod
    def _get_timeline_data(ward, suggestions):
        def _get_room(assignment):
            if suggestion := next(
                (s for s in suggestions if s.get("assignmentId") == assignment.id), None
            ):
                return suggestion["roomId"]

            if assignment.bed:
                return assignment.bed.room.id

            return "unassigned"

        hospital_stays = [
            {
                "id": assignment.id,
                "content": assignment.medical_record.patient.short_info
                + (
                    f"<br/>+ {_('accompanying person')}"
                    if assignment.accompanied
                    else ""
                ),
                "start": str(assignment.admission_date),
                "end": str(assignment.discharge_date),
                "requiredBeds": 2 if assignment.accompanied else 1,
                "group": _get_room(assignment),
                "className": assignment.medical_record.patient.gender,
                "dataAttributes": "all",
                "style": f"height: {'73px' if assignment.accompanied else '32px'};",
            }
            for assignment in BedAssignment.objects.filter(
                Q(discharge_date__gt=current_or_travelled_time())
                & (Q(recommended_ward=ward) | Q(recommended_ward__isnull=True))
            )
        ]
        groups = [
            {
                "id": room.id,
                "content": f"{_('Room')} {room.room_number}<br><span>({room.total_beds} {_('beds')})</span>",
                "beds": room.total_beds,
            }
            for room in ward.rooms.all()
        ] + [{"id": "unassigned", "content": _("unassigned")}]

        return {"items": json.dumps(hospital_stays), "groups": json.dumps(groups)}

    def post(self, request, *args, **kwargs):
        r"""
        Method to bulk-save bed assignments submitted through the timeline

        :param request: The current request
        :type request: ~django.http.HttpRequest

        :param \*args: The supplied arguments
        :type \*args: list

        :param \**kwargs: The supplied keyword arguments
        :type \**kwargs: dict

        :return: Redirect to list of wards
        :rtype: ~django.http.HttpResponseRedirect
        """
        changes = json.loads(request.POST.get("timeline_changes"))
        assignments = BedAssignment.objects.filter(
            id__in=[change["assignmentId"] for change in changes]
        ).order_by("admission_date")

        failed_counter = 0
        for assignment in assignments:
            # unassign the current bed, in case it interferes with another assignment and this assignment goes wrong
            assignment.bed = None
            assignment.save()

            change = next(
                item for item in changes if item.get("assignmentId") == assignment.id
            )
            if change["roomId"] == "unassigned":
                continue

            room = Room.objects.get(id=change["roomId"])
            conflicts = room.beds.filter(
                Q(
                    (
                        Q(assignments__discharge_date__gte=assignment.admission_date)
                        & Q(assignments__admission_date__lte=assignment.discharge_date)
                    )
                    | (
                        Q(assignments__admission_date__lte=assignment.discharge_date)
                        & Q(assignments__discharge_date__gte=assignment.admission_date)
                    )
                )
            )
            if not (beds := room.beds.exclude(pk__in=conflicts)):
                failed_counter += 1
                continue

            assignment.bed = beds.first()
            assignment.save()

        if len(changes) != failed_counter:
            messages.success(
                request,
                _("{} of {} assignments have successfully been saved.").format(
                    len(changes) - failed_counter, len(changes)
                ),
            )
        if failed_counter:
            messages.error(
                request,
                _("{} assignments failed. The patients have been unassigned.").format(
                    failed_counter
                ),
            )

        return redirect("cms:protected:timeline", pk=kwargs.get("pk"))
