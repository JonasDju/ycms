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
    // refresh initial value
    ageSlider.dispatchEvent(new Event("input"));

    // Handle fetching ward's discharge policy on selection
    const wardSelection = document.querySelector("#id_recommended_ward") as HTMLSelectElement;
    const wardDischargeRoot = document.querySelector("#id_ward_discharge_policy") as HTMLDivElement;
    const wardDischargeInfo = document.querySelector("#id_ward_discharge_policy_text") as HTMLDivElement;

    const infoBoxBlue = ["text-blue-800", "bg-blue-50", "dark:text-blue-400"];
    const infoBoxRed = ["text-red-800", "bg-red-50", "dark:text-red-400"];

    let weekdayNamesLong = [];

    /* eslint-disable-next-line @typescript-eslint/no-explicit-any */
    const setWardDischargeInfo = (json: any) => {
        if (Object.keys(json).length === 0) {
            wardDischargeRoot.classList.add("hidden");
            return;
        }

        // store localized weekday names to be used in info boxes below discharge date
        weekdayNamesLong = json.weekdays_long;

        let res = json.info_text[0];
        const numAllowedDays = json.allowed_weekdays_short.length;
        if (numAllowedDays === 0) {
            wardDischargeRoot.classList.remove(...infoBoxBlue);
            wardDischargeRoot.classList.add(...infoBoxRed);
        } else {
            wardDischargeRoot.classList.remove(...infoBoxRed);
            wardDischargeRoot.classList.add(...infoBoxBlue);

            json.allowed_weekdays_short.forEach((day: string, index: number) => {
                res += ` ${day}`;
                if (index === numAllowedDays - 2) {
                    // second to last day in list gets suffix "and"
                    res += ` ${json.info_text[1]}`;
                } else if (index === numAllowedDays - 1) {
                    // last day gets suffix "."
                    res += ".";
                } else {
                    res += ",";
                }
            });
        }

        wardDischargeRoot.classList.remove("hidden");
        wardDischargeInfo.textContent = res;
    };

    const getNextValidDischargeDate = (date: Date, mask: number) => {
        /* eslint-disable no-magic-numbers, no-bitwise */
        const dayOfWeek = (((date.getDay() - 1) % 7) + 7) % 7;
        for (let i = 1; i < 7; i++) {
            if ((mask >> (dayOfWeek + i) % 7) & 0b1) {
                const nextDate = new Date(date);
                nextDate.setDate(date.getDate() + i);
                return nextDate;
            }
        }
        /* eslint-enable no-magic-numbers, no-bitwise */

        return null;
    };

    const dischargeInvalidDiv = document.querySelector("#intake-info-discharge-invalid") as HTMLElement;
    const dischargeInvalidText = document.querySelector("#intake-info-discharge-invalid-text") as HTMLElement;
    const dischargeValidDiv = document.querySelector("#intake-info-discharge-valid") as HTMLElement;
    const dischargeDateInput = document.querySelector("#id_discharge_date") as HTMLInputElement;
    const moveDischargeDateBtn = document.querySelector("#intake-discharge-move-btn") as HTMLButtonElement;

    // TODO: validation when changing discharge through number of nights input
    const validateDate = () => {
        const dateString = dischargeDateInput.value;
        // no date entered, or no ward set
        if (!dateString || !dischargeInvalidText.hasAttribute("mask") || weekdayNamesLong.length === 0) {
            dischargeInvalidDiv.classList.add("hidden");
            dischargeValidDiv.classList.add("hidden");
            return;
        }

        // validate discharge date against mask
        const date = new Date(dateString);
        /* eslint-disable-next-line no-magic-numbers */
        const dayOfWeek = (((date.getDay() - 1) % 7) + 7) % 7; // JS Date starts at Sunday=0, but need Monday=0
        const mask = Number(dischargeInvalidText.getAttribute("mask"));
        /* eslint-disable-next-line no-bitwise */
        const dischargeValid = (mask >> dayOfWeek) & 0b1;

        if (dischargeValid) {
            dischargeInvalidDiv.classList.add("hidden");
            dischargeValidDiv.classList.remove("hidden");
        } else {
            // TODO: translation
            const selectedDay = new Intl.DateTimeFormat("en-US", { weekday: "long" }).format(date);
            const nextPossibleDischargeDate = getNextValidDischargeDate(date, mask);
            if (nextPossibleDischargeDate) {
                dischargeInvalidText.textContent = `Discharges not allowed on ${selectedDay}.\n
                Next possible discharge date is ${nextPossibleDischargeDate.toDateString()}.`;
                moveDischargeDateBtn.textContent = `Move discharge to ${nextPossibleDischargeDate.toDateString()}.`;
                // TODO: store discharge date, so wont need to be recalculated on button press
                // moveDischargeDateBtn.setAttribute("moveTo", nextPossibleDischargeDate);
                moveDischargeDateBtn.classList.remove("hidden");
            } else {
                dischargeInvalidText.textContent = `Discharges not allowed on ${selectedDay}.\n
                No next discharge date available in this ward.`;
                moveDischargeDateBtn.classList.add("hidden");
            }

            dischargeInvalidDiv.classList.remove("hidden");
            dischargeValidDiv.classList.add("hidden");
        }
    };

    wardSelection.addEventListener("change", () => {
        if (!wardSelection.value) {
            // hide info text field
            wardDischargeRoot.classList.add("hidden");
            dischargeInvalidText.removeAttribute("mask");
            // hide feedback for discharge validity
            dischargeInvalidDiv.classList.add("hidden");
            dischargeValidDiv.classList.add("hidden");
        } else {
            // fetch ward's allowed discharge days, display in info text
            const url = `/intake/allowed-discharge-days/?q=${encodeURIComponent(wardSelection.value)}`;

            fetch(url)
                .then((response) => response.json())
                .then((json) => {
                    setWardDischargeInfo(json);
                    // store mask for validation
                    dischargeInvalidText.setAttribute("mask", json.mask);
                    validateDate();
                });
        }
    });

    moveDischargeDateBtn.addEventListener("click", () => {
        const currentDate = new Date(dischargeDateInput.value);
        const mask = Number(dischargeInvalidText.getAttribute("mask"));

        if (currentDate && mask) {
            // TODO: update with formatted string since .valueAsDate sets UTC date
            // TODO: fetch stored moveTo date
            dischargeDateInput.valueAsDate = getNextValidDischargeDate(currentDate, mask);
            // TODO: update number of nights field
            // const durationInput = document.querySelector("#input-patient-intake-stay-duration") as HTMLInputElement;
            // durationInput.value =
            // TODO: if user changed discharge by offset (number of nights field), save this value so it will be used again when intake date changes
            // TODO: revalidate or somehow give feedback for successful moving of discharge date
            validateDate();
        }
    });

    // when discharge date changes, recheck validity wrt ward's policy
    document.querySelector("#id_discharge_date")?.addEventListener("change", validateDate);

    // If a patient was passed to the intake form, use it
    const urlParams = new URLSearchParams(window.location.href);
    if (urlParams.get("patient") && existingPatientSelect) {
        existingPatientSelect.dispatchEvent(new Event("change"));
    }
});
