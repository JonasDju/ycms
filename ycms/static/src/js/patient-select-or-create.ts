window.addEventListener("load", () => {
    const patientInputs = Array.from(
        document.querySelectorAll<HTMLInputElement>(".patient-option input, .patient-option select") || [],
    );

    // subform divs
    const emergencyIntakeForms = [<HTMLInputElement>document.querySelector("#emergency-intake")];
    const normalIntakeForms = Array.from(
        document.querySelectorAll<HTMLInputElement>("#existing-patient, #new-patient") || [],
    );

    // input/select fields
    const existingPatientInputs = Array.from(
        document.querySelectorAll<HTMLInputElement>("#existing-patient select, #existing-patient input") || [],
    );
    const existingPatientSelect = <HTMLSelectElement>document.querySelector("#id_patient");
    const newPatientInputs = Array.from(document.querySelectorAll<HTMLInputElement>("#new-patient input") || []);
    const unknownPatientInputs = Array.from(
        document.querySelectorAll<HTMLInputElement>("#emergency-intake input") || [],
    );

    const firstNameField = <HTMLInputElement>document.querySelector("#id_first_name");
    const lastNameField = <HTMLInputElement>document.querySelector("#id_last_name");
    const genderFields = document.querySelectorAll<HTMLInputElement>("input[name='gender']");
    const dateOfBirthField = <HTMLInputElement>document.querySelector("#id_date_of_birth");
    const insuranceFields = document.querySelectorAll<HTMLInputElement>("input[name='insurance_type']");

    /* eslint-disable-next-line @typescript-eslint/no-explicit-any */
    const fillPatientFields = (json: any) => {
        if (Object.keys(json).length === 0) {
            // clear
            firstNameField.value = "";
            lastNameField.value = "";
            genderFields.forEach((radio) => {
                /* eslint-disable-next-line no-param-reassign */
                radio.checked = false;
            });
            dateOfBirthField.value = "";
            insuranceFields.forEach((radio) => {
                /* eslint-disable-next-line no-param-reassign */
                radio.checked = false;
            });
        } else {
            firstNameField.value = json.first_name;
            lastNameField.value = json.last_name;

            for (const radio of genderFields) {
                if (radio.value === json.gender) {
                    radio.checked = true;
                    break;
                }
            }

            dateOfBirthField.valueAsDate = new Date(json.date_of_birth);

            if (json.insurance_type) {
                insuranceFields[1].checked = true;
            } else {
                insuranceFields[0].checked = true;
            }
        }
    };

    // Handle selecting an existing patient
    // -> disables fields for creatinga new patient and fills them with the existing values
    if (existingPatientSelect) {
        existingPatientSelect.addEventListener("change", () => {
            const patientSelected = !!existingPatientSelect.value;
            newPatientInputs.forEach((input) => {
                /* eslint-disable-next-line no-param-reassign */
                input.disabled = patientSelected;
                // save state in DOM (needed to reconstruct state after intake mode switch)
                existingPatientSelect.setAttribute("patient-selected", patientSelected.toString());
            });

            // fetch patient's data and fill out fields in new patient form
            if (patientSelected) {
                const patientId = existingPatientSelect.value;

                const url = `/autocomplete/patient-details/?q=${encodeURIComponent(patientId)}`;

                fetch(url)
                    .then((response) => response.json())
                    .then((json) => fillPatientFields(json));
            } else {
                // clear fields
                fillPatientFields({});
            }
        });
    }

    const intakeModeLabels = document.querySelectorAll(`label[for="intake-mode-switch"]`);
    const classLabelNormal = "font-normal text-gray-700 my-3 mx-2";
    const classLabelHighlighted = "font-normal text-blue-600 my-3 mx-2";

    // Handle hiding and disabling fields in respective intake mode
    const intakeModeSwitch = <HTMLInputElement>document.querySelector("#intake-mode-switch");

    if (intakeModeSwitch) {
        intakeModeSwitch.addEventListener("change", () => {
            const inEmergencyMode = intakeModeSwitch.checked;
            intakeModeLabels[0].className = inEmergencyMode ? classLabelNormal : classLabelHighlighted;
            intakeModeLabels[1].className = inEmergencyMode ? classLabelHighlighted : classLabelNormal;
            // show/hide forms
            /* eslint-disable no-param-reassign */
            normalIntakeForms.forEach((form) => {
                form.style.display = inEmergencyMode ? "none" : "";
            });
            emergencyIntakeForms.forEach((form) => {
                form.style.display = inEmergencyMode ? "" : "none";
            });

            // disable hidden input fields; will not be sent with POST
            existingPatientInputs.forEach((input) => {
                input.disabled = inEmergencyMode;
            });
            newPatientInputs.forEach((input) => {
                // disable if in emergency intake mode or existing patient was selected prior
                input.disabled = inEmergencyMode || existingPatientSelect.getAttribute("patient-selected") === "true";
                input.required = !inEmergencyMode;
            });
            unknownPatientInputs.forEach((input) => {
                input.disabled = !inEmergencyMode;
                input.required = inEmergencyMode;
            });
            /* eslint-enable no-param-reassign */
        });
        // update dom according to current state of mode switch
        // TODO: may pass argument for initial intake mode from view
        intakeModeSwitch.dispatchEvent(new Event("change"));
    }

    // Handle resetting all patient selection input fields
    const resets = document.querySelectorAll<HTMLElement>(".form-reset");
    resets.forEach((reset) => {
        reset.addEventListener("click", () => {
            patientInputs.forEach((input) => {
                /* eslint-disable-next-line no-param-reassign */
                input.value = input.defaultValue;
                /* eslint-disable-next-line no-param-reassign */
                input.disabled = false;
            });
            resets.forEach((reset) => {
                reset.classList.add("hidden");
            });
        });
    });

    // Handle displaying and updating the selected approximate age of emergency patients
    const ageSlider = document.querySelector("#id_unknown-approximate_age") as HTMLInputElement;
    const ageDisplay = document.querySelector("#approximate-age-display") as HTMLElement;
    if (!ageSlider || !ageDisplay) {
        return;
    }
    ageSlider.addEventListener("input", () => {
        ageDisplay.innerHTML = ageSlider.value;
    });

    // If a patient was passed to the intake form, use it
    const urlParams = new URLSearchParams(window.location.href);
    if (urlParams.get("patient") && existingPatientSelect) {
        existingPatientSelect.dispatchEvent(new Event("change"));
    }
});
