from django.test import TestCase

from .models import Patient, ICD10Entry, MedicalRecord, BedAssignment, User

from pathlib import Path
import pandas as pd
import os
import json
import logging

from ..core.settings import BASE_DIR
from .import_data import import_data

tmp_csv = Path("./", "test_patients.csv")

class CsvUploadTest(TestCase):
    def setUp(self):
        # create an example csv file
        test_patients = {
            "Nachname": ["Kuhn", "Schulte", "Schilling"],
            "Vorname": ["Christine", "Kirsten", "Franziska"],
            "Privatpatient": ["P", "P", ""],
            "mit_Begleitperson": [0, 0, 0],
            "Erstellungsdatum": ["23.11.2024 16:07", "22.11.2024 23:55", "01.12.2024 15:59"],
            "Aufnahmedatum": ["24.11.2024 12:00", "23.11.2024 12:00", "02.12.2024 12:00"],
            "Entlassdatum": ["27.11.2024 10:00", "04.12.2024 10:00", "06.12.2024 10:00"],
            "Geschlecht": ["W", "W", "W"],
            "Alter_bei_Aufnahme": [29, 44, 46],
            "Diagnosekatalog": ["ICD10_2019", "ICD10_2019", "ICD10_2019"],
            "Diagnosecode": ["J86.9", "N40", "L71.1"],
            }
        df = pd.DataFrame(test_patients)
        df.to_csv(tmp_csv, index=False)
    
        # create a root user 
        with open(Path(BASE_DIR, "cms/fixtures/hospital_data.json")) as f:
            hospital_data = json.load(f)
            root_user = hospital_data[0]["fields"]
            personnel_id, email, job_type, first_name, last_name = root_user["personnel_id"], root_user["email"], root_user["job_type"], root_user["first_name"], root_user["last_name"]
            group = ""
            User.objects.create(personnel_id=personnel_id, email=email, job_type=job_type, first_name=first_name, last_name=last_name)
        

    def test_upload_patients(self):
        """
        Method to test file upload functionality
        """
        user = User.objects.get(personnel_id="ROOT_00001")
        import_result = import_data(csv_file=tmp_csv, user=user)
        self.assertEqual(import_result["error"], None)
        self.assertEqual(Patient.objects.all().count(), 3)
        self.assertEqual(ICD10Entry.objects.all().count(), 3)
        self.assertEqual(MedicalRecord.objects.all().count(), 3)
        self.assertEqual(BedAssignment.objects.all().count(), 3)

    def tearDown(self):
        os.remove(tmp_csv)