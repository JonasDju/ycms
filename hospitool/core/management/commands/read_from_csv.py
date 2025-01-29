import csv
import json
import logging
import os
import random
from datetime import datetime, timedelta

from django.conf import settings
from django.core import serializers
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandParser
from django.utils.dateparse import parse_date, parse_datetime

from ....cms.models import (
    Bed,
    BedAssignment,
    ICD10Entry,
    MedicalRecord,
    Patient,
    Room,
    User,
    Ward,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Management Command to load new test data
    """

    help = "parse new test data and store in fixture"

    @staticmethod
    def _vorname(gender):
        with open(
            "hospitool/core/management/commands/res/firstnames.json", "r", encoding="utf-8"
        ) as file:
            data = json.load(file)
            return random.choice(data[gender.upper()]).strip()

    @staticmethod
    def _nachname():
        with open(
            "hospitool/core/management/commands/res/lastnames.txt", "r", encoding="utf-8"
        ) as file:
            data = file.readlines()
            return random.choice(data).strip()

    @staticmethod
    def _dob(age):
        current_year = datetime.now().year
        random_year = current_year - int(age)
        random_month = random.randint(3, 10)
        random_day = random.randint(1, (28 if random_month in [2, 4, 6, 9, 11] else 31))

        random_date = datetime(random_year, random_month, random_day)
        return random_date.strftime("%Y-%m-%d")

    @staticmethod
    def _fix_time(time, rounded=False, offset=0):
        original = datetime.strptime(time, "%d.%m.%Y %H:%M")
        if rounded:
            original = original.replace(minute=0)
        if offset:
            original = original + timedelta(hours=1)
        return f"{str(original.isoformat())}Z"

    def _clean_patient(self, patient, pseudonymized):
        gender = "f" if patient["Geschlecht"] == "W" else "m"
        return {
            "gender": gender,
            "first_name": self._vorname(gender)
            if pseudonymized
            else patient["Vorname"],
            "last_name": self._nachname() if pseudonymized else patient["Nachname"],
            "_first": patient["Vorname"] if pseudonymized else "",
            "_last": patient["Nachname"] if pseudonymized else "",
            "date_of_birth": self._dob(patient["Alter_bei_Aufnahme"]),
            "insurance_type": bool(patient["Privatpatient"]),
            "diagnosis_code": patient["Diagnosecode"],
            "accompanied": bool(int(patient["mit_Begleitperson"])),
            "created_at": self._fix_time(patient["Erstellungsdatum"]),
            "admission_date": self._fix_time(patient["Aufnahmedatum"], True, 1),
            "discharge_date": self._fix_time(patient["Entlassdatum"], True, 0),
        }

    def add_arguments(self, parser: CommandParser) -> None:
        """
        Define the arguments of this command

        :param parser: The argument parser
        """
        parser.add_argument("source", help="The source CSV file location", nargs=1)
        parser.add_argument("target", help="The target JSON file location", nargs=1)
        parser.add_argument(
            "ward_name",
            help="Name of the ward to create (optional)",
            nargs="?",
            default="",
        )
        parser.add_argument(
            "rooms",
            help="The source JSON file for the rooms (optional)",
            nargs="?",
            default=None,
        )
        parser.add_argument(
            "--pseudonymized",
            help="Set flag if names are pseudonymized in the source file",
        )

    # pylint: disable=arguments-differ,too-many-locals
    def handle(
        self, source, target, ward_name, rooms, *args, pseudonymized=False, **options
    ) -> None:
        r"""
        Command to read from the given CSV, turn the data into database objects,
        and store those objects in a fixture for reuse.

        Usage instructions:
        - use ./tools/prune_database.sh
        - comment out all data loading in ./tools/loadtestdata.sh expect for hospital_data.json
        - use this script as shown below

        Example usage:
        ./tools/hospitool-cli read_from_csv raw_data.csv test_data.json Intensivmedizin rooms.json --pseudonymized True

        :param source: The source file
        :type source: str
        :param target: The target file
        :type target: str
        :param ward_name: The name of the ward to create
        :type ward_name: str
        :param rooms: The rooms file
        :type rooms: str or None
        :param \*args: The supplied arguments
        :param pseudonymized: If names are pseudonymized in source file
        :type pseudonymized: bool
        :param \**options: The supplied keyword options
        """
        source = source[0]
        target = target[0]

        objects = []

        # Attempt to load the rooms. Fallback to ward 1 otherwise.
        if ward_name and rooms:
            creator = User.objects.get(id=2)
            ward = Ward.objects.create(
                creator=creator, ward_number=ward_name.lower(), floor=1, name=ward_name
            )
            objects.append(ward)

            with open(rooms, "r", encoding="utf-8") as file:
                rooms_data = json.loads(file.read())["rooms"]

            for room_data in rooms_data:
                room = Room.objects.create(
                    ward=ward, creator=creator, room_number=room_data["name"]
                )
                objects.append(room)
                for _ in range(room_data["capacity"]):
                    bed = Bed.objects.create(
                        room=room, creator=creator, bed_type="normal"
                    )
                    objects.append(bed)
        else:
            ward = Ward.objects.get(id=1)

        # Get all patients and codes
        codes = []
        patients = []
        with open(source, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for line in reader:
                patient = self._clean_patient(line, pseudonymized)
                codes.append(patient["diagnosis_code"])
                patients.append(patient)

        logger.info("%s new patients to create", len(patients))

        # If the code is new, create it
        code_objects = []
        call_command("loaddata", "hospitool/cms/fixtures/icd10_data.json")
        for code in codes:
            if not (entry := ICD10Entry.objects.filter(code=code).first()):
                description = input(f'Add missing description for "{code}": ')
                entry = ICD10Entry.objects.create(code=code, description=description)
            code_objects.append(entry)

        logger.info("%s codes collected", len(code_objects))

        # Create the patients
        creator = User.objects.get(id=4)

        for patient in patients:
            p = Patient.objects.create(
                creator=creator,
                created_at=parse_datetime(patient["created_at"]),
                insurance_type=patient["insurance_type"],
                first_name=patient["first_name"],
                _first=patient["_first"],
                last_name=patient["last_name"],
                _last=patient["_last"],
                gender=patient["gender"],
                date_of_birth=parse_date(patient["date_of_birth"]),
            )

            mr = MedicalRecord.objects.create(
                creator=creator,
                created_at=parse_datetime(patient["created_at"]),
                patient=p,
                diagnosis_code=ICD10Entry.objects.filter(
                    code=patient["diagnosis_code"]
                ).first(),
                record_type="intake",
            )

            ba = BedAssignment.objects.create(
                creator=creator,
                created_at=parse_datetime(patient["created_at"]),
                admission_date=parse_datetime(patient["admission_date"]),
                discharge_date=parse_datetime(patient["discharge_date"]),
                accompanied=patient["accompanied"],
                medical_record=mr,
                recommended_ward=ward,
            )

            objects.append(p)
            objects.append(mr)
            objects.append(ba)

        logger.info("done creating patients")

        # Save the new data
        with open(target, "w", encoding="utf-8") as file:
            file.write(serializers.serialize("json", objects))
        with open(
            f"{target.split('.json')[0]}_icd10.json", "w", encoding="utf-8"
        ) as file:
            file.write(serializers.serialize("json", code_objects))
        with open(
            os.path.join(settings.BASE_DIR, "cms", "fixtures", "icd10_data.json"),
            "w",
            encoding="utf-8",
        ) as file:
            file.write(serializers.serialize("json", ICD10Entry.objects.all()))

        logger.info("done saving new objects")
