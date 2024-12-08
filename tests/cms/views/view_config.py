# Copyright [2019] [Integreat Project]
# Copyright [2023] [YCMS]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
This modules contains the config for the view tests
"""
import json

from ...conftest import MEDICAL_PERSONNEL, ROLES, ROOT, STATION_MANAGEMENT, ZBM

#: This list contains the config for all views
#: Each element is a tuple which consists of two elements: A list of view configs and the keyword arguments that are
#: identical for all views in this list. Each view config item consists of the name of the view, the list of roles that
#: are allowed to access that view and optionally post data that is sent with the request. The post data can either be
#: a dict to send form data or a string to send JSON.
VIEWS = [
    (
        [
            ("cms:protected:patients", [ROOT, STATION_MANAGEMENT, MEDICAL_PERSONNEL]),
            (
                "cms:protected:create_patient",
                [ROOT, MEDICAL_PERSONNEL],
                {
                    "first_name": "Firstname",
                    "last_name": "Lastname",
                    "insurance_type": True,
                    "date_of_birth": "2023-01-01",
                    "gender": "d",
                },
            ),
            ("cms:protected:intake", [ROOT, MEDICAL_PERSONNEL]),
            (
                "cms:protected:intake",
                [ROOT, MEDICAL_PERSONNEL],
                {
                    "patient": 1,
                    "diagnosis_code": "80173",
                    "admission_date": "2023-02-01T11:42:11.331Z",
                    "discharge_date": "2023-02-08T11:42:11.331Z",
                },
            ),
            (
                "cms:protected:intake",
                [ROOT, MEDICAL_PERSONNEL],
                {
                    "first_name": "Firstname",
                    "last_name": "Lastname",
                    "insurance_type": True,
                    "date_of_birth": "2023-01-01",
                    "gender": "d",
                    "diagnosis_code": "80173",
                    "admission_date": "2023-02-01T11:42:11.331Z",
                    "discharge_date": "2023-02-08T11:42:11.331Z",
                    "accompanied": True,
                    "note": "test note",
                },
            ),
            (
                "cms:protected:intake",
                [ROOT, MEDICAL_PERSONNEL],
                {
                    "unknown-gender": "d",
                    "unknown-approximate_age": "30",
                    "diagnosis_code": "80173",
                    "admission_date": "2023-02-01T11:42:11.331Z",
                    "discharge_date": "2023-02-08T11:42:11.331Z",
                    "accompanied": False,
                },
            ),
            ("cms:protected:ward_management", [ROOT, ZBM]),
            (
                "cms:protected:ward_management",
                [ROOT, ZBM],
                {"floor": 2, "name": "Testward", "nickname": "TW"},
            ),
            (
                "cms:protected:ward_management",
                [ROOT, ZBM],
                {
                    "floor": 2,
                    "name": "Testward",
                    "nickname": "TW",
                    "rooms": json.dumps(
                        {
                            "room_1": ["normal", "small"],
                            "room_2": ["ventilator"],
                            "room_3": [],
                        }
                    ),
                },
            ),
        ],
        {},
    ),
    (
        [
            (
                "cms:protected:update_patient",
                [ROOT, STATION_MANAGEMENT, MEDICAL_PERSONNEL],
                {"gender": "f"},
            ),
            (
                "cms:protected:delete_patient",
                [ROOT, STATION_MANAGEMENT, MEDICAL_PERSONNEL],
                {"post": ""},
            ),
        ],
        {"pk": 1},
    ),
    (
        [
            (
                "cms:protected:patient_details",
                [ROOT, STATION_MANAGEMENT, MEDICAL_PERSONNEL],
            ),
            (
                "cms:protected:create_record",
                [ROOT, MEDICAL_PERSONNEL],
                {"record_type": "lab", "note": "test note"},
            ),
        ],
        {"pk": 1},
    ),
    (
        [
            (
                "cms:protected:ward_detail",
                [ROOT, STATION_MANAGEMENT, MEDICAL_PERSONNEL],
            ),
            (
                "cms:protected:ward_detail",
                [ROOT, STATION_MANAGEMENT, MEDICAL_PERSONNEL],
                {"ward": 1},
            ),
            (
                "cms:protected:mode_switch",
                [ROOT, STATION_MANAGEMENT, MEDICAL_PERSONNEL],
                {"post": ""},
            ),
            ("cms:protected:timeline", [ROOT, STATION_MANAGEMENT, MEDICAL_PERSONNEL]),
            (
                "cms:protected:timeline",
                [ROOT, STATION_MANAGEMENT, MEDICAL_PERSONNEL],
                {
                    "timeline_changes": json.dumps(
                        [
                            {"assignmentId": 1, "roomId": 1},
                            {"assignmentId": 2, "roomId": "unassigned"},
                        ]
                    )
                },
            ),
        ],
        {"pk": 1},
    ),
    (
        [
            (
                "cms:protected:update_intake",
                [ROOT, STATION_MANAGEMENT, MEDICAL_PERSONNEL],
                {
                    "record_type": "intake",
                    "note": "test note",
                    "diagnosis_code": "80173",
                    "admission_date": "2023-01-01T11:42:11.331Z",
                    "accompanied": True,
                },
            ),
            (
                "cms:protected:cancel_stay",
                [ROOT, STATION_MANAGEMENT, MEDICAL_PERSONNEL],
                {"post": ""},
            ),
        ],
        {"pk": 1},
    ),
    (
        [
            (
                "cms:protected:discharge_patient",
                [ROOT, STATION_MANAGEMENT, MEDICAL_PERSONNEL],
                {"next": ""},
            )
        ],
        {"assignment_id": 1},
    ),
    (
        [
            (
                "cms:protected:assign_patient",
                [ROOT, STATION_MANAGEMENT, MEDICAL_PERSONNEL],
            ),
            (
                "cms:protected:assign_patient",
                [ROOT, STATION_MANAGEMENT, MEDICAL_PERSONNEL],
                {"next": ""},
            ),
        ],
        {"ward_id": 1, "assignment_id": 1},
    ),
    (
        [
            (
                "cms:protected:assign_patient",
                [ROOT, STATION_MANAGEMENT, MEDICAL_PERSONNEL],
                {"next": "", "new_ward": 2},
            )
        ],
        {"ward_id": 1, "assignment_id": 1},
    ),
    (
        [
            ("cms:protected:autocomplete_icd10", ROLES, {"q": "M2"}),
            ("cms:protected:autocomplete_patient", ROLES, {"q": "Per"}),
            ("change-theme", ROLES, {"post": ""}),
        ],
        {},
    ),
    ([("switch-language", ROLES, {"post": ""})], {"language_code": "en"}),
    (
        [
            ("cms:protected:create_user", [ROOT, ZBM, STATION_MANAGEMENT]),
            (
                "cms:protected:create_user",
                [ROOT, ZBM, STATION_MANAGEMENT],
                {
                    "personnel_id": "ABCDE12345",
                    "email": "test@ycms.de",
                    "job_type": "DOCTOR",
                    "first_name": "First",
                    "last_name": "Last",
                    "assigned_ward": 1,
                    "group": "MEDICAL_PERSONNEL",
                },
            ),
        ],
        {},
    ),
]

#: In order for these views to be used as parameters, we have to flatten the nested structure
PARAMETRIZED_VIEWS = [
    (view_name, kwargs, post_data[0] if post_data else {}, roles)
    for view_conf, kwargs in VIEWS
    for view_name, roles, *post_data in view_conf
]
