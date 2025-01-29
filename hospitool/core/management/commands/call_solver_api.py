import json
import logging
import os
import subprocess

from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandParser

from ....cms.models import BedAssignment, Ward
from ....cms.models.timetravel_manager import current_or_travelled_time

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Management Command to call the external PRA solver
    """

    help = "use the PRA solver to suggest an assignment for the given ward"

    @staticmethod
    def _gender(g):
        gender_map = {"m": "M", "f": "W", "d": "D"}
        return gender_map[g]

    def _discretize(self, date):
        timedelta = date - self.now.replace(minute=0, second=0, microsecond=0)
        hours = max(0, timedelta.seconds // 3600 + timedelta.days * 24)

        self.max_hour = max(self.max_hour, hours)
        return hours

    @staticmethod
    def _call_solver(last_hour):
        script = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "call_solver.sh"
        )
        with open(os.devnull, "wb") as devnull:
            subprocess.call(
                [script, settings.PRA_BASE, "generated", str(last_hour)], stdout=devnull
            )

    def add_arguments(self, parser: CommandParser) -> None:
        """
        Define the arguments of this command

        :param parser: The argument parser
        """
        parser.add_argument(
            "ward_id", help="ID of the ward which should be exported", nargs=1
        )

    def __init__(self, *args, **kwargs):
        self.now = current_or_travelled_time()
        self.max_hour = 0
        super().__init__(*args, **kwargs)

    # pylint: disable=arguments-differ
    def handle(self, ward_id, *args, **options) -> None:
        r"""
        Command to export bed assignments of the given ward

        :param ward_id: The ward ID
        :type ward_id: int
        :param \*args: The supplied arguments
        :param \**options: The supplied keyword options
        """
        ward = Ward.objects.get(pk=ward_id[0])

        objects = (
            BedAssignment.objects.filter(
                discharge_date__gt=self.now, recommended_ward=ward
            )
            .prefetch_related("medical_record__patient")
            .all()
        )

        instance = {
            "patients": [
                {
                    "id": str(obj.id),
                    "age": obj.medical_record.patient.age,
                    "sex": self._gender(obj.medical_record.patient.gender),
                    "isPrivate": obj.medical_record.patient.insurance_type,
                    "companion": obj.accompanied,
                    "registration": 0,
                    "admission": self._discretize(obj.admission_date),
                    "discharge": self._discretize(obj.discharge_date) + 1,
                }
                for obj in objects
            ],
            "rooms": [
                {"name": str(room.id), "capacity": room.total_beds - room.total_blocked_beds}
                for room in ward.rooms.all()
            ],
            "currentPatientAssignment": {
                str(assignment.id): str(assignment.bed.room.id)
                for assignment in objects
                if assignment.bed
            },
        }

        with open(settings.PRA_INPUT_PATH, "w", encoding="utf-8") as file:
            file.write(json.dumps(instance))

        self._call_solver(self.max_hour + 1)

        # If the output file does not exist, the algorithm failed to execute or
        # did not find a feasible solution
        if not os.path.exists(settings.PRA_OUTPUT_PATH):
            return ""

        with open(settings.PRA_OUTPUT_PATH, "r", encoding="utf-8") as file:
            patient_assignments = json.loads(file.read())["patient_assignments"]

        # Remove the file once it is parsed to make sure that it is not read again
        # the next time the algorithm fails
        os.remove(settings.PRA_OUTPUT_PATH)

        # The solver does not indicate if an assignment has remained unchanged,
        # and python dicts are a unhashable type, so we have to do this manually
        previous_assignment_hashes = [
            f"{assignment}:{room}"
            for assignment, room in instance["currentPatientAssignment"].items()
        ]

        solution = [
            {
                "assignmentId": int(id),
                "roomId": int(rooms[0]["roomName"]) if rooms[0] else "unassigned",
            }
            for id, rooms in patient_assignments.items()
            if f"{id}:{rooms[0]['roomName']}" not in previous_assignment_hashes
        ]

        return json.dumps(solution)
