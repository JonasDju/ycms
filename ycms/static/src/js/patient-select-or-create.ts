window.addEventListener("load", () => {
    // subform divs
    const emergencyIntakeForms = [<HTMLInputElement>document.querySelector("#emergency-intake")];
    const normalIntakeForms = Array.from(
        document.querySelectorAll<HTMLInputElement>("#existing-patients, #new-patient") || [],
    );

    // toggle for intake mode (normal/emergency)
    const intakeModeSwitch = <HTMLInputElement>document.querySelector("#intake-mode-switch");

    const submissionButton = document.querySelector("#submit-button") as HTMLButtonElement;

    // input/select fields
    const newPatientInputs = Array.from(document.querySelectorAll<HTMLInputElement>("#new-patient input") || []);
    const unknownPatientInputs = Array.from(
        document.querySelectorAll<HTMLInputElement>("#emergency-intake input") || [],
    );

    // fields for new/existing patients
    const firstNameField = <HTMLInputElement>document.querySelector("#id_first_name");
    const lastNameField = <HTMLInputElement>document.querySelector("#id_last_name");
    const newPatientGenderFields = document.querySelectorAll<HTMLInputElement>("#new-patient input[name='gender']");
    const dateOfBirthField = <HTMLInputElement>document.querySelector("#id_date_of_birth");
    const insuranceFields = document.querySelectorAll<HTMLInputElement>("input[name='insurance_type']");

    const patientSearchStatus = <HTMLDivElement>document.querySelector("#patient-search-status span");

    const selectedPatientIdEl = document.querySelector("#selected-patient-id") as HTMLInputElement;
    const cancelSelectionBtn = document.querySelector("#cancel-selection-button") as HTMLButtonElement;

    // fields for unknown (emergency) intake patient
    const ageSlider = document.querySelector("#id_unknown-approximate_age") as HTMLInputElement;
    const ageDisplay = document.querySelector("#approximate-age-display") as HTMLElement;
    const unknownPatientGenderFields = document.querySelectorAll<HTMLInputElement>("#emergency-intake input[name='gender']")

    const clearPatientButtons = Array.from(document.querySelectorAll<HTMLButtonElement>(".clear-patient-button") || []);

    /**
     * Formats a string with replacement values with placeholders '{}' or '{placeholderName}'. 
     * If an object is passed with values, looks up the placeholder names as keys on the object.
     * @param template The format string.
     * @param values The replacements for the placeholder values.
     * @returns The formatted string.
     */
    function formatString(template: string, values: Record<string, any> | any[]): string {
        if (Array.isArray(values)) {
            return template.replace(/{(\w*)}/g, () => values.shift());
        }
        return template.replace(/{(\w+)}/g, (_, key) => values[key]);
    }

    /* eslint-disable-next-line @typescript-eslint/no-explicit-any */
    function fillPatientFields(patientData: any) {
        if (Object.keys(patientData).length === 0) {
            throw new Error(`Patient data passed to fill in patient fields is empty. ${patientData}`);
        } else {
            firstNameField.value = patientData.first_name;
            lastNameField.value = patientData.last_name;
            
            for (const radio of newPatientGenderFields) {
                if (radio.value === patientData.gender) {
                    radio.checked = true;
                    break;
                }
            }
            
            dateOfBirthField.valueAsDate = new Date(patientData.date_of_birth);
            
            if (patientData.insurance_type) {
                insuranceFields[1].checked = true;
            } else {
                insuranceFields[0].checked = true;
            }
        }
    };

    /**
     * Highlights the passed element as selected in the existing patients list.
     * If no element is given, deselects all list elements.
     * @param listElement The element to select or null.
     */
    function selectPatientListElement(listElement: HTMLElement | null) {
        const patientsList = document.querySelector("#existing-patients-list");

        // deselect current selection
        patientsList?.querySelectorAll(":scope > [data-selected]").forEach(s => {
            s.removeAttribute("data-selected");
        });

        // select new element
        listElement?.setAttribute("data-selected", "");
    };

    /**
     * Stores the current entries of the patient inputs in data attributes so they can be restored later
     */
    function storePatientInputs() {
        newPatientInputs.forEach(input => {
            // for radio fields, store their checked attribute
            if (input.type.toLowerCase() === "radio") {
                input.setAttribute("data-old-checked", input.checked.toString());
            } else {
                input.setAttribute("data-old-value", input.value);
            }
        });
    };

    /**
     * Restores previously saved patient inputs and deletes the storage attributes.
     * Keeps present values if no stored value exists.
     */
    function restorePatientInputs() {
        newPatientInputs.forEach(input => {
            // for radio fields, relevant attribute is "checked" 
            if (input.type.toLowerCase() === "radio") {
                input.checked = (input.getAttribute("data-old-checked") ?? input.checked.toString()) === "true";
                input.removeAttribute("data-old-checked");
            } else {
                input.value = input.getAttribute("data-old-value") ?? input.value;
                input.removeAttribute("data-old-value");
            }
        });
    };

    /**
     * Creates an element for an existing patient in the list of existing patients matching the current inputs.
     * @param patient_stub Object containing the patient id and a name used as label in the list.
     */
    function createExistingPatientListElement(patient_stub: any): HTMLElement {
        const patientPrototype = document.querySelector("#patient-select-prototype");

        const listEntry = patientPrototype?.cloneNode(true) as HTMLElement;
        const listEntryText = listEntry.querySelector("span") as HTMLElement;

        listEntryText.textContent = patient_stub.name;
        listEntry.id = `patient-select-${patient_stub.id}`;
        listEntry.classList.remove("!hidden", "hidden");

        // on click fetch patient data and update visualization of list
        listEntry.addEventListener("click", () => {
            // fetch first, update once fetch is returned
            const url = `/autocomplete/patient-details/?q=${encodeURIComponent(patient_stub.id)}`;
            
            // click on already selected element should not refetch data
            if (selectedPatientIdEl.value === patient_stub.id) return;

            fetch(url)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error when fetching patient data for id ${patient_stub.id}, status:${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    // is this the first selection (after possibly clearing)
                    const isFirstSelection = selectedPatientIdEl.value === "";

                    // store newly selected patient id
                    selectedPatientIdEl.value = patient_stub.id;
                    
                    if (isFirstSelection) {
                        // store inputs made by user so they can be restored after cancelling selection
                        storePatientInputs();
                        // disable input fields (were enabled previously)
                        updateInputsEnabledState();
                        // update submit button text (was "create patient previously")
                        updateSubmitButton();
                        // enable cancel selection button
                        cancelSelectionBtn.classList.remove("hidden");
                    }

                    // update patient fields
                    fillPatientFields(data);
                    // show as selected
                    selectPatientListElement(listEntry);

                })
                .catch(error => {
                    console.error(`Error in fetching patient data: ${error}`);
                });
            
        });

        return listEntry;
    };

    /**
     * Creates a list of selectable patients for the results in a fetch request for patients matching the curring inputs.
     * @param data The patient stubs (id and name/label) for which to create the list elements.
     */
    function createExistingPatientsList(data: any) {
        const existingPatientsList = document.querySelector("#existing-patients-list");
        // clear previous suggestions, except first one (template)
        existingPatientsList?.replaceChildren(existingPatientsList.firstElementChild as Node);
        
        data.forEach((patient: any) => {
            existingPatientsList?.appendChild(createExistingPatientListElement(patient));
        });
    };

    let currentController: AbortController | null = null; // AbortController of current patients fetch request

    const handleNameInputs = () => {
        const lastNameQuery = lastNameField.value.trim();
        const firstNameQuery = firstNameField.value.trim();
        
        // limit search to not execute with few characters so backend query doesn't take too long
        if (lastNameQuery.length + firstNameQuery.length < 3) {
            // TODO: translate
            patientSearchStatus.textContent = "Enter at least 3 characters to search.";
            return;
        }

        const queryUrl = `/autocomplete/patient/?lastName=${encodeURIComponent(lastNameQuery)}&firstName=${encodeURIComponent(firstNameQuery)}`;
        
        // abort previous fetch request
        if (currentController) {
            currentController.abort();
        }

        currentController = new AbortController();
        const signal = currentController.signal;

        fetch(queryUrl, { signal })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status:${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                createExistingPatientsList(data.results);
                if (data.num_results > 0) {
                    // TODO: show text informing that there are more matches than displayed
                    // TODO translation
                    patientSearchStatus.textContent = `Found ${data.num_results} matches.`;
                } else {
                    // TODO translation
                    patientSearchStatus.textContent = "No matches found";
                }
            })
            .catch(error => {
                if (error.name === "AbortError") {
                    console.log("Request aborted.");
                } else {
                    console.error("Error fetching search results:", error);
                }
            });
    };

    lastNameField?.addEventListener("input", handleNameInputs);
    firstNameField?.addEventListener("input", handleNameInputs);

    // cancels the current existing patient selection if there is any
    const cancelSelection = () => {
        // deselect all
        selectPatientListElement(null);
        // clear stored patient id 
        selectedPatientIdEl.value = "";
        // pop previous user inputs back into input fields
        restorePatientInputs();
        // enable input fields again
        updateInputsEnabledState();
        // hide cancel selection button
        cancelSelectionBtn?.classList.add("hidden");
        // update submit button to show "intake for new patient" again
        updateSubmitButton();
    };

    cancelSelectionBtn?.addEventListener("click", cancelSelection);

    /**
     * Clears the inputs of the current intake mode
     * @param button The button element 
     */
    function clearPatientFields(button: HTMLButtonElement) {
        // root div of the form that this button is a part of
        const formDiv = button.closest(".intake-option");

        const isNewPatientClear = formDiv && formDiv.id === "new-patient";

        // if new patient inputs are to be cleared, also cancel the current selection
        // this call also enables the inputs again (if disabled)
        if (isNewPatientClear) {
            cancelSelection();
        }

        // reset values for all inputs of the parent form
        formDiv?.querySelectorAll("input").forEach(input => {
            if (input.type.toLowerCase() === "radio") {
                input.checked = false;
            } else {
                input.value = input.defaultValue;
            }
        });

        // age display value needs to be updated manually
        if (!isNewPatientClear) {
            updateAgeDisplay();
        }
    };

    clearPatientButtons.forEach(btn => btn.addEventListener("click", () => clearPatientFields(btn)));

    /**
     * Initializes the intake forms with patient data if one was passed to this view.
     */
    function initWithExistingPatient() {
        const url = `/autocomplete/patient-details/?q=${encodeURIComponent(selectedPatientIdEl.value)}`;

        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error when fetching initial patient data for id ${selectedPatientIdEl.value}, status:${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // create list element and show as selected
                const patient_stub = { id: selectedPatientIdEl.value, name: `${data.last_name}, ${data.first_name}, ${data.date_of_birth}` };
                const listEl = createExistingPatientListElement(patient_stub);
                document.querySelector("#existing-patients-list")?.appendChild(listEl);

                selectPatientListElement(listEl);

                // fill input values
                fillPatientFields(data);

                // enable cancel selection button
                cancelSelectionBtn.classList.remove("hidden");
                // disable input fields
                updateInputsEnabledState();
                // update submit button text
                updateSubmitButton();
            })
            .catch(error => {
                console.error(`Encountered error when initializing page with initial patient ${error}`);
            });
    };

    /**
     * Enables/Disables patient input fields based on current view configuration and hides/shows the respective forms.
     * I.e. in emergency intake mode disables all fields for new patient and hides the form along with the existing patients list.
     */
    function updateInputsEnabledState() {
        // in emergency intake mode?
        if (intakeModeSwitch.checked) {
            normalIntakeForms.forEach(form => form.classList.add("hidden"));
            emergencyIntakeForms.forEach(form => form.classList.remove("hidden"));

            // disable appropriate input fields so they are not sent with POST
            selectedPatientIdEl.disabled = true;
            
            newPatientInputs.forEach(input => input.disabled = true);
            unknownPatientInputs.forEach(input => input.disabled = false);
        } else {
            normalIntakeForms.forEach(form => form.classList.remove("hidden"));
            emergencyIntakeForms.forEach(form => form.classList.add("hidden"));

            // disable appropriate input fields so they are not sent with POST
            selectedPatientIdEl.disabled = false;
            
            // keep patient inputs disabled if there was an existing patient selected
            newPatientInputs.forEach(input => input.disabled = selectedPatientIdEl.value !== "");
            unknownPatientInputs.forEach(input => input.disabled = true);
        }
        
    };

    /**
     * Updates the text of the submit button to provide information on the action that will be executed.
     */
    function updateSubmitButton() {
        // translated strings are given by data-message-X in template patient_intake_form.html
        // in emergency intake mode?
        if (intakeModeSwitch.checked) {
            submissionButton.textContent = submissionButton.dataset.messageEmergency || submissionButton.textContent;
        } else if (selectedPatientIdEl.value === "") {
            submissionButton.textContent = submissionButton.dataset.messageNewPatient || submissionButton.textContent;
        } else {
            submissionButton.textContent = submissionButton.dataset.messageExistingPatient || submissionButton.textContent;
        }
    };

    const intakeModeLabels = document.querySelectorAll(`label[for="intake-mode-switch"]`);
    const classLabelNormal = "font-normal text-gray-700 my-3 mx-2";
    const classLabelHighlighted = "font-normal text-blue-600 my-3 mx-2";

    if (intakeModeSwitch) {
        intakeModeSwitch.addEventListener("change", () => {
            const inEmergencyMode = intakeModeSwitch.checked;
            // TODO: refactor style definitions into DOM
            intakeModeLabels[0].className = inEmergencyMode ? classLabelNormal : classLabelHighlighted;
            intakeModeLabels[1].className = inEmergencyMode ? classLabelHighlighted : classLabelNormal;
            
            // show/hide respective forms and enable/disable input fields
            updateInputsEnabledState();

            // update text of submission button
            updateSubmitButton();
        });

        // update dom according to current state of mode switch
        intakeModeSwitch.dispatchEvent(new Event("change"));
    }

    // Handle displaying and updating the selected approximate age of emergency patients
    const updateAgeDisplay = () => {
        if (ageDisplay && ageSlider) {
            ageDisplay.textContent = ageSlider.value;
        }
    };

    ageSlider?.addEventListener("input", updateAgeDisplay);
    ageSlider?.dispatchEvent(new Event("input")); // set initial value

    // If a patient was passed to the intake form, use it
    const urlParams = new URLSearchParams(window.location.href);
    if (urlParams.get("patient")) {
        initWithExistingPatient();
    }
});
