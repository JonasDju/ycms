import logging

import pandas as pd
from datetime import datetime
from pathlib import Path

from .models import Patient, ICD10Entry, MedicalRecord, BedAssignment
from .constants.gender import MALE, FEMALE, DIVERSE

logger = logging.getLogger(__name__)

def import_data(csv_file, user, val_sep=","):
    """
    Import patient data from a .csv file into the database
    The .csv file needs to be in the following format:
    last_name,first_name,private_insurance,accompanied,created_at,admission_date,
    discharge_date,gender,age_at_arrival,diagnosis_catalogue,diagnosis_code

    :param csv_file: file path of the csv file
    :type csv_file: pathlib.Path

    :param user: user that imports/creates new entries
    :type user: django.contrib.auth.models.User

    :param val_sep: separator used in csv file
    :type val_sep: String

    :return: error indicator and number of imported objects per model
    :rtype: dict
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

    result = {
        "error": None,
        "patient_count": 0,
        "diagnosis_code_count": 0,
        "medical_record_count": 0,
        "bed_assignment_count": 0,
    }

    try:
        df = pd.read_csv(csv_file, sep=val_sep)
    except Exception as e:
        logger.error(f"Failed to read csv file from path {csv_file}")
        logger.error(f"Exception:\n{e}")
        result["error"] = -1
        return result
    
    if not all(column in df.columns.to_list() for column in default_columns.values()):
        logger.error("CSV file does not contain all required column labels!")
        result["error"] = -2
        return result
    
    imported_entries = {
        "patient": [],
        "diagnosis_code": [],
        "medical_record": [],
        "bed_assignment": [],
    }

    logger.debug(f"User importing data: {user}")

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
            
            # extract datetime objects from strings
            created_at=datetime.strptime(patient_entry[default_columns["created_at"]], "%d.%m.%Y %H:%M")
            admission_date=datetime.strptime(patient_entry[default_columns["admission_date"]], "%d.%m.%Y %H:%M")
            discharge_date=datetime.strptime(patient_entry[default_columns["discharge_date"]], "%d.%m.%Y %H:%M")


            imported_patient, newly_created_patient = Patient.objects.get_or_create(
                creator=user,
                created_at=created_at,
                #updated_at=created_at, # left out to indicate time of import
                insurance_type=insurance_type,
                first_name=patient_entry[default_columns["first_name"]],
                last_name=patient_entry[default_columns["last_name"]],
                gender=gender,
                date_of_birth=date_of_birth,
                _first="",
                _last="",
            )
            if newly_created_patient:
                imported_entries["patient"].append(imported_patient.pk)
                logger.debug(f"Created new patient (pk: {imported_patient.pk})")
            else:
                logger.debug(
                    f"Patient \"{patient_entry[default_columns["last_name"]]}, "
                    + f"{patient_entry[default_columns["first_name"]]}\" already existed (pk: {imported_patient.pk})"
                )

            imported_diagnosis_code, newly_created_diagnosis_code = ICD10Entry.objects.get_or_create(
                code=patient_entry[default_columns["diagnosis_code"]],
                #description="", # field not provided in csv
            )
            if newly_created_diagnosis_code:
                imported_entries["diagnosis_code"].append(imported_diagnosis_code.pk)
                logger.debug(f"Created new diagnosis code (pk: {imported_diagnosis_code.pk})")
            else:
                logger.debug(
                    f"Diagnosis Code \"{patient_entry[default_columns["diagnosis_code"]]}\" "
                    + f"already existed (pk: {imported_diagnosis_code.pk})"
                )

            imported_medical_record, newly_created_medical_record = MedicalRecord.objects.get_or_create(
                creator=user,
                created_at=created_at,
                #updated_at=created_at, # left out to indicate time of import
                patient=imported_patient,
                diagnosis_code=imported_diagnosis_code,
                record_type="intake", # adopted from "read_from_csv"
                #note="", # field not provided in csv
            )
            if newly_created_medical_record:
                imported_entries["medical_record"].append(imported_medical_record.pk)
                logger.debug(f"Created new medical record (pk: {imported_medical_record.pk})")
            else:
                logger.debug(
                    f"Medical record for patient \"{patient_entry[default_columns["last_name"]]}, "
                    + f"{patient_entry[default_columns["first_name"]]}\" already existed (pk: {imported_medical_record.pk})"
                )

            imported_bed_assignment, newly_created_bed_assignment = BedAssignment.objects.get_or_create(
                creator=user,
                created_at=created_at,
                #updated_at=created_at, # left out to indicate time of import
                admission_date=admission_date,
                discharge_date=discharge_date,
                accompanied=accompanied,
                medical_record=imported_medical_record,
            )
            if newly_created_bed_assignment:
                imported_entries["bed_assignment"].append(imported_bed_assignment.pk)
                logger.debug(f"Created new bed assignment (pk: {imported_bed_assignment.pk})")
            else:
                logger.debug(
                    f"Bed assignment for patient \"{patient_entry[default_columns["last_name"]]}, "
                    + f"{patient_entry[default_columns["first_name"]]}\" between {patient_entry[default_columns["admission_date"]]} "
                    + f"and {patient_entry[default_columns["discharge_date"]]} already existed (pk: {imported_medical_record.pk})"
                )
        except Exception as e:
            logger.error(f"Error occured in row {index+1}.\nException:")
            logger.error(e)
            Patient.objects.filter(pk__in=imported_entries["patient"]).delete()
            ICD10Entry.objects.filter(pk__in=imported_entries["diagnosis_code"]).delete()
            MedicalRecord.objects.filter(pk__in=imported_entries["medical_record"]).delete()
            BedAssignment.objects.filter(pk__in=imported_entries["bed_assignment"]).delete()
            logger.error("Deleted the already imported data, no new data was inserted")
            result["error"] = index+1
            return result
    
    result["patient_count"] = len(imported_entries["patient"])
    result["diagnosis_code_count"] = len(imported_entries["diagnosis_code"])
    result["medical_record_count"] = len(imported_entries["medical_record"])
    result["bed_assignment_count"] = len(imported_entries["bed_assignment"])
    logger.debug(
        "Successfully imported data"
        f"New patients created: {result["patient_count"]}"
        f"New diagnosis codes created: {result["diagnosis_code_count"]}"
        f"New medical records created: {result["medical_record_count"]}"
        f"New bed assignments created: {result["bed_assignment_count"]}"
    )
    return result # Import finished successfully
