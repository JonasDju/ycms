from django.test import TestCase

from pathlib import Path
import pandas as pd
import os

from .import_data import import_data


class CsvUploadTest(TestCase):
    def test_upload_patients():
        """
        Method to test file upload functionality
        """
        # first create a csv file from an example dataframe that can be passed to the import function
        test_patients = {
            "Nachname": ["Kuhn, Schulte, Schilling"],
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
        tmp_path = Path("./temp")
        tmp_path.mkdir(parents=True, exist_ok=True)
        tmp_csv = Path(tmp_path, "test_patients.csv")
        df.to_csv(tmp_csv, index=False)

        # TODO handle exception or error cases, check if upload was successful and patients were added to database
        import_data(csv_path=tmp_csv)
        os.remove(tmp_csv)
        print("The test \"test_upload_patients\" finished (hopefully) successful")
