import logging

import pandas as pd
from datetime import datetime
from pathlib import Path

from cms.models import patient, ICD10Entry, medical_record, bed_assignment
from cms.constants import MALE, FEMALE, DIVERSE

logger = logging.getLogger(__name__)

def import_data(csv_path, val_sep=","):
    """
    Import patient data from a .csv file into the database
    The .csv file needs to be in the following format:
    last_name,first_name,private_insurance,accompanied,created_at,admission_date,
    discharge_date,gender,age_at_arrival,diagnosis_catalogue,diagnosis_code

    :param csv_path: file path of the csv file
    :type csv_path: pathlib.Path
    :param val_sep: separator used in csv file
    :type val_sep: String
    """
    
    default_columns={
        "last_name": "Nachname",
        "first_name": "Vorname",
        "insurance_type": "Privatpatient",
        "accompanied": "mit_Begleitperson",
        "created_at": "Erstellungsdatum",
        "admission_date": "Aufnahmedatum",
        "discharge_date": "Entlassdatum",
        "gender": "Geschlecht",
        "age_at_arrival": "Alter_bei_Aufnahme",
        "diagnosis_catalog": "Diagnosekatalog",
        "diagnosis_code": "Diagnosecode"
    }

    try:
        df = pd.read_csv(csv_path, sep=val_sep)
    except:
        logger.error(f"Failed to read csv file from path {csv_path}")
        # TODO gracefully handle error case, inform user about faulty csv file
        return
    
    if not df.columns.to_list()==list(default_columns.values()):
        logger.warning("Column names of csv file do not match default names!")
    
    for (index, patient_entry) in df.iterrows():
        try:
            # attributes "accompanied" and "insurance_type" have to be infered from non-Bool values
            accompanied = patient_entry[default_columns["accompanied"]] > 0 
            insurance_type = patient_entry[default_columns["insurance_type"]] == "P"

            # by default, set date_of_birth to January 1st as only the age at arrival is provided
            year_of_birth = datetime.now().year - patient_entry[default_columns["age_at_arrival"]]
            date_of_birth = f"{year_of_birth}-01-01"

            # extract gender
            if patient_entry[default_columns["gender"]] in ["M","m"]:
                gender = MALE
            elif patient_entry[default_columns["gender"]] in ["F", "f", "W", "w"]:
                gender = FEMALE
            elif patient_entry[default_columns["gender"]] in ["D", "d"]:
                gender = DIVERSE
            else:
                logger.warning("Value for gender not recognized, default to diverse")
                gender = DIVERSE


            imported_patient = patient(
                created_at=patient_entry[default_columns["created_at"]],
                #updated_at=patient_entry[default_columns["created_at"]], # left out to indicate time of import
                insurance_type=insurance_type,
                first_name=patient_entry[default_columns["first_name"]],
                last_name=patient_entry[default_columns["last_name"]],
                gender=gender,
                date_of_birth=date_of_birth,
                _first="",
                _last="",
            )
            imported_patient.save()

            imported_diagnosis_code = ICD10Entry(
                code=patient_entry[default_columns["diagnosis_code"]],
                description="", # field not provided in csv
            )

            imported_medical_record = medical_record(
                created_at=patient_entry[default_columns["created_at"]],
                #updated_at=patient_entry[default_columns["created_at"]], # left out to indicate time of import
                patient=imported_patient,
                diagnosis_code=imported_diagnosis_code,
                record_type="intake", # adopted from "read_from_csv"
                note="",
            )
            imported_medical_record.save()

            imported_bed_assignment = bed_assignment(
                created_at=patient_entry[default_columns["created_at"]],
                #updated_at=patient_entry[default_columns["created_at"]], # left out to indicate time of import
                admission_date=datetime.strptime(patient_entry[default_columns["admission_date"]], "%d.%m.%Y %H:%M"),
                discharge_date=datetime.strptime(patient_entry[default_columns["discharge_date"]], "%d.%m.%Y %H:%M"),
                accompanied=accompanied,
                medical_record=imported_medical_record,
            )
            imported_bed_assignment.save()
        except Exception as e:
            logger.error(f"Error occured in row {index+1}.\nException:")
            logger.error(e)
