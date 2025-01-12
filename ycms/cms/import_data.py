import logging

import pandas as pd
from datetime import datetime
from pathlib import Path

from django.utils.translation import gettext as _

from .models import Patient, ICD10Entry, MedicalRecord, BedAssignment, Floor, Ward, Room, Bed
from .constants.gender import MALE, FEMALE, DIVERSE

logger = logging.getLogger(__name__)

def import_data(csv_file, user, data_to_import, val_sep=","):
    """
    Import patient data from a .csv file into the database
    The .csv file needs to be in the following format:
    last_name,first_name,private_insurance,accompanied,created_at,admission_date,
    discharge_date,gender,age_at_arrival,diagnosis_catalogue,diagnosis_code

    :param csv_file: file path of the csv file
    :type csv_file: pathlib.Path

    :param user: user that imports/creates new entries
    :type user: django.contrib.auth.models.User

    :param data_to_import: number between 1 and 5 indicating categories of data to import
    :type data_to_import: String

    :param val_sep: separator used in csv file
    :type val_sep: String

    :return: error indicator and number of imported objects per model
    :rtype: dict
    """
    logger.debug("Start patient data import")

    result = {
        "error_code": None,
        "error_msg": "",
        "new_entry_count": 0,
        "duplicate_entry_count": 0,
        "updated_entry_count": 0
    }

    try:
        df = pd.read_csv(csv_file, sep=val_sep)
    except Exception as e:
        logger.error(f"Failed to read csv file from path {csv_file}")
        logger.error(f"Exception:\n{e}")
        result["error_code"] = -1
        result["error_msg"] = _("The CSV file could not be read.")
        return result
    
    category_columns = {
        "patient":["last_name", "first_name", "insurance_type", "gender", "age_at_arrival"],
        "medical_record":["diagnosis_catalog", "diagnosis_code"],
        "bed_assignment":["admission_date", "discharge_date", "accompanied"],
        "ward":["recommended_ward", "floor"],
        "bed": ["bed_type", "room_number"]
    }
    categories = ["patient", "medical_record", "bed_assignment", "ward", "bed"]

    column_name = {
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
        "diagnosis_code": "Diagnosecode",
        "recommended_ward": "Station",
        "floor": "Stockwerk",
        "bed_type": "Betttyp",
        "room_number": "Raumnummer"
    }
    
    # select data to import depending on user input
    to_import = {"patient": True, "medical_record": False, "bed_assignment": False, "ward": False, "bed": False}
    for category_level in range(int(data_to_import)):
        to_import[categories[category_level]] = True
    logger.debug(f"to import: {to_import}")
    
    provided_columns = df.columns.to_list()
    missing_columns = []
    for category in category_columns:
        if to_import[category]:
            for column in category_columns[category]:
                if column_name[column] not in provided_columns:
                    missing_columns.append(column_name[column])
    if missing_columns:
        logger.error("CSV file does not contain all required column labels for selected categories!")
        logger.error(f"Missing columns: " + ", ".join(missing_columns))
        result["error_code"] = -2
        result["error_msg"] = _("Missing columns: ") + ", ".join(missing_columns)
        return result
            
    # alternative solution however unpreferred, as creation date might be necessary to uniquely identify a patient
    # make column "created_at" optional and choose current time if not provided in file
    #creation_date = column_name["created_at"] in df.columns.to_list()
    import_time = datetime.now()
    
    imported_entries = {
        "patient": [],
        "diagnosis_code": [],
        "medical_record": [],
        "bed_assignment": [],
    }
    updated_entries = {
        "ward": [],
        "bed": [],
    }

    duplicate_count = 0 # number of entries in the file that already existed in the database
    update_count = 0 # number of entries in the file that were used to update existing entries in the database

    logger.debug(f"User importing data: {user}")

    for (index, patient_entry) in df.iterrows():
        # prepare detecting duplicates and updates
        newly_created_medical_record = newly_created_bed_assignment = updated_bed_assignment = False
        try:
            # attribute "insurance_type" has to be infered from non-Bool value
            insurance_type = patient_entry[column_name["insurance_type"]] in ["P", "p"]            

            # by default, set date_of_birth to January 1st as only the age at arrival is provided (same as in )
            year_of_birth = datetime.now().year - patient_entry[column_name["age_at_arrival"]]
            date_of_birth = f"{year_of_birth}-01-01"

            # extract gender
            if patient_entry[column_name["gender"]] in ["M","m"]:
                gender = MALE
            elif patient_entry[column_name["gender"]] in ["F", "f", "W", "w"]:
                gender = FEMALE
            elif patient_entry[column_name["gender"]] in ["D", "d"]:
                gender = DIVERSE
            else:
                logger.warning("Value for gender not recognized, default to diverse")
                gender = DIVERSE
            
            # extract provided creation time or select current time of import
            created_at=datetime.strptime(patient_entry[column_name["created_at"]], "%d.%m.%Y %H:%M")# if creation_date else import_time


            imported_patient, newly_created_patient = Patient.objects.get_or_create(
                created_at=created_at,
                insurance_type=insurance_type,
                first_name=patient_entry[column_name["first_name"]],
                last_name=patient_entry[column_name["last_name"]],
                gender=gender,
                date_of_birth=date_of_birth,
                defaults={
                    "creator":user,
                    "updated_at":created_at,
                    "_first":"",
                    "_last":"",
                }
            )
            if newly_created_patient:
                imported_entries["patient"].append(imported_patient.pk)
                logger.debug(f"Created new patient (pk: {imported_patient.pk})")
            else:
                logger.debug(
                    f"Patient \"{patient_entry[column_name["last_name"]]}, "
                    + f"{patient_entry[column_name["first_name"]]}\" already existed (pk: {imported_patient.pk})"
                )

            if to_import["medical_record"]:
                imported_diagnosis_code, newly_created_diagnosis_code = ICD10Entry.objects.get_or_create(
                    code=patient_entry[column_name["diagnosis_code"]],
                    defaults={
                        "description":""
                    }
                )
                if newly_created_diagnosis_code:
                    imported_entries["diagnosis_code"].append(imported_diagnosis_code.pk)
                    logger.debug(f"Created new diagnosis code (pk: {imported_diagnosis_code.pk})")
                else:
                    logger.debug(
                        f"Diagnosis Code \"{patient_entry[column_name["diagnosis_code"]]}\" "
                        + f"already existed (pk: {imported_diagnosis_code.pk})"
                    )

                imported_medical_record, newly_created_medical_record = MedicalRecord.objects.get_or_create(
                    patient=imported_patient,
                    diagnosis_code=imported_diagnosis_code,
                    defaults={
                        "creator":user,
                        "created_at":created_at,
                        "updated_at":import_time,
                        "record_type":"intake", # adopted from "read_from_csv"
                        "note":""
                    }
                )
                if newly_created_medical_record:
                    imported_entries["medical_record"].append(imported_medical_record.pk)
                    logger.debug(f"Created new medical record (pk: {imported_medical_record.pk})")
                else:
                    logger.debug(
                        f"Medical record for patient \"{patient_entry[column_name["last_name"]]}, "
                        + f"{patient_entry[column_name["first_name"]]}\" already existed (pk: {imported_medical_record.pk})"
                    )

                if to_import["bed_assignment"]:
                    # attribute "accompanied" has to be infered from non-Bool value
                    accompanied = patient_entry[column_name["accompanied"]] > 0 
                    # extract datetime objects from strings
                    admission_date=datetime.strptime(patient_entry[column_name["admission_date"]], "%d.%m.%Y %H:%M")
                    discharge_date=datetime.strptime(patient_entry[column_name["discharge_date"]], "%d.%m.%Y %H:%M")
                    
                    
                        
                    imported_bed_assignment, newly_created_bed_assignment = BedAssignment.objects.get_or_create(
                        admission_date=admission_date,
                        discharge_date=discharge_date,
                        accompanied=accompanied,
                        medical_record=imported_medical_record,
                        defaults={
                            "creator":user,
                            "created_at":created_at,
                            "updated_at":created_at,
                        }
                    )

                    if to_import["ward"] and imported_bed_assignment.recommended_ward == None:
                        floor_name = patient_entry[column_name["floor"]]
                        floor = Floor.objects.get(
                            name=floor_name
                        )
                        ward_name = patient_entry[column_name["recommended_ward"]]
                        ward = Ward.objects.get(
                            floor=floor,
                            name=ward_name
                        )                            
                    elif to_import["bed"]:
                        ward = imported_bed_assignment.recommended_ward
                    
                    # if bed is already assigned, do not search for another one as no further might be available leading to a false exception
                    if to_import["bed"] and imported_bed_assignment.bed == None:
                        room_number = patient_entry[column_name["room_number"]]
                        logger.debug(f"Entered room number: {room_number}")
                        room = Room.objects.get(
                            room_number=room_number,
                            ward=ward
                        )
                        logger.debug(f"Room found: {room}")
                        # TODO ensure uniqueness of beds (at least in same room) in model
                        # TODO requires unique names of beds/bed spaces
                        bed_type = patient_entry[column_name["bed_type"]]
                        logger.debug(f"Entered bed type: {bed_type}")
                        # TODO preferred solution as soon as there is a unique bed_space_name
                        # bed = Bed.objects.get(
                        #     bed_type=bed_type,
                        #     bed_space_name=bed_space_name,
                        #     room=room
                        # )
                        # TODO current solution: choose any existing available bed
                        beds = Bed.objects.filter(
                            bed_type=bed_type,
                            room=room
                        )
                        logger.debug(f"Found {len(beds)} beds in {room}")
                        # Check if there is any bed of the given type in the room
                        if not beds:
                            raise Exception(f"Found no bed with bed_type {bed_type} in {room}")
                        # Check if any of the filtered beds is available and choose the first one
                        # TODO this does not check for already assigned accompanied patients and thus might "overassign" beds
                        # room.available_beds does not help as it relies on bed.is_available which relies on current_or_travelled_time
                        # therefore we would need to check all timely relevant bed_assignments of beds in this room to see whether there
                        # are assigned accompanied patients
                        # Furthermore, if the current patient is accompanied, we need to check for an additional bed
                        for bed in beds:
                            logger.debug(f"Checking {bed} for conflicts")
                            conflicting_assignments = BedAssignment.objects.filter(
                                bed=bed,
                                admission_date__lt=discharge_date,
                                discharge_date__gt=admission_date
                            )
                            if not conflicting_assignments:
                                break
                        else:
                            raise Exception(f"Found no available bed with bed_type {bed_type} in {room}")
                        # end of current solution
                        logger.debug(f"Found bed: {bed}")                            

                    if newly_created_bed_assignment:
                        # not a fancy solution to set ward and or bed here but at least consistent with below
                        if to_import["ward"]:
                            imported_bed_assignment.recommended_ward = ward
                            if to_import["bed"]:
                                imported_bed_assignment.bed = bed
                            imported_bed_assignment.save()
                        imported_entries["bed_assignment"].append(imported_bed_assignment.pk)
                        logger.debug(f"Created new bed assignment (pk: {imported_bed_assignment.pk})")
                    else:
                        # bed_assignment can already exist without ward and bed and thus might be updated with new information
                        if to_import["ward"] and imported_bed_assignment.recommended_ward == None:
                            imported_bed_assignment.recommended_ward = ward
                            updated_entries["ward"].append(imported_bed_assignment.pk)
                            updated_bed_assignment = True
                        if to_import["bed"] and imported_bed_assignment.bed == None:
                            imported_bed_assignment.bed = bed
                            updated_entries["bed"].append(imported_bed_assignment.pk)
                            updated_bed_assignment = True
                        if updated_bed_assignment:
                            imported_bed_assignment.save()
                            logger.debug(
                                f"Bed assignment for patient \"{patient_entry[column_name["last_name"]]}, "
                                + f"{patient_entry[column_name["first_name"]]}\" between {patient_entry[column_name["admission_date"]]} "
                                + f"and {patient_entry[column_name["discharge_date"]]} was updated (pk: {imported_medical_record.pk})"
                            )
                        else:
                            logger.debug(
                                f"Bed assignment for patient \"{patient_entry[column_name["last_name"]]}, "
                                + f"{patient_entry[column_name["first_name"]]}\" between {patient_entry[column_name["admission_date"]]} "
                                + f"and {patient_entry[column_name["discharge_date"]]} already existed (pk: {imported_medical_record.pk})"
                            )
        except Exception as e:
            logger.error(f"Error occured in row {index+1}.\nException:")
            logger.error(e)
            # Delete all newly created objects
            Patient.objects.filter(pk__in=imported_entries["patient"]).delete()
            ICD10Entry.objects.filter(pk__in=imported_entries["diagnosis_code"]).delete()
            MedicalRecord.objects.filter(pk__in=imported_entries["medical_record"]).delete()
            BedAssignment.objects.filter(pk__in=imported_entries["bed_assignment"]).delete()
            # If bed_assignments were updated (existing bed_assignment with value None for ward and/or bed), reset updated fields to None
            BedAssignment.objects.filter(pk__in=updated_entries["ward"]).update(recommended_ward=None)
            BedAssignment.objects.filter(pk__in=updated_entries["bed"]).update(bed=None)
            logger.error("Deleted the already imported data, no new data was inserted")
            result["error_code"] = index+1
            result["error_msg"] = _("An error occured when importing entry no. {}.").format(
                    result["error_code"]
                )
            result["duplicate_entry_count"] = result["updated_entry_count"] = 0
            return result
        if not newly_created_patient:
            if not newly_created_medical_record and not newly_created_bed_assignment and not updated_bed_assignment:
                duplicate_count+=1
            else:
                update_count+=1
    
    result["new_entry_count"] = len(imported_entries["patient"])
    result["duplicate_entry_count"] = duplicate_count
    result["updated_entry_count"] = update_count
    logger.debug(
        "Successfully imported data "
        + f"New patients created: {result["new_entry_count"]} "
        + f"New diagnosis codes created: {len(imported_entries["diagnosis_code"])} "
        + f"New medical records created: {len(imported_entries["medical_record"])} "
        + f"New bed assignments created: {len(imported_entries["bed_assignment"])} "
        + f"Duplicate entries found: {result['duplicate_entry_count']} "
        + f"Existing entries updated: {result['updated_entry_count']}"
    )
    return result # Import finished successfully
