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
    const existingPatientSelect = <HTMLSelectElement>document.querySelector("#existing-patient select");
    const newPatientInputs = Array.from(document.querySelectorAll<HTMLInputElement>("#new-patient input") || []);
    const unknownPatientInputs = Array.from(
        document.querySelectorAll<HTMLInputElement>("#emergency-intake input") || [],
    );

    // Handle disabling new patient inputs and filling with patient's data if existing patient has been selected
    // BUG: nextSibling does not work since the tomselect does not yet exist...
    // if (existingPatientInput && existingPatientInput.nextSibling) {

    //     const classObserver = new MutationObserver((mutations) => {
    //         mutations.forEach(mu => {
    //             console.log("mutation callback");
    //             if (mu.type !== "attributes" && mu.attributeName !== "class") return;
    //             const existingInputFilled = existingPatientInput.classList.contains("has-items");
    //             // some patient is selected
    //             newPatientInputs.forEach((input) => {
    //                 input.disabled = !existingInputFilled;
    //             });
    //             console.log("classes changed");
    //             console.log(existingPatientInput.classList);

    //             // TODO: fetch patient's data and fill out fields in new patient form
    //             // or somehow get the reference to the tomselect instance
    //         });
    //     });

    //     console.log(classObserver);

    //     classObserver.observe(existingPatientInput.nextSibling, { attributes: true });
    // }

    // Handle disabling all relevant inputs if one patient selection method has been interacted with
    // patientInputs.forEach((input) => {
    //     input.addEventListener("change", () => {
    //         const siblings = Array.from(
    //             input.closest(".patient-option")?.querySelectorAll<HTMLInputElement>("input, select") || [],
    //         );
    //         patientInputs.forEach((otherInput) => {
    //             if (!siblings.includes(otherInput)) {
    //                 /* eslint-disable-next-line no-param-reassign */
    //                 otherInput.disabled = true;
    //             }
    //         });

    //         const reset = input.closest(".patient-option")?.querySelector(".form-reset") as HTMLElement;
    //         reset.classList.remove("hidden");
    //     });
    // });

    // Handle disabling new patient inputs when an existing patient has been selected
    const initialPatientSelection = () => {
        // get patient selection div where we can track if an item is selected
        const patientSelectDiv = existingPatientSelect.parentElement?.querySelector(".ts-wrapper");

        // div has not been initialized yet (tomselect instance created in autocomplete.ts)
        // this may happen if the existing patient field gets pre-populated on site load
        if (!patientSelectDiv) {
            newPatientInputs.forEach((input) => {
                /* eslint-disable-next-line no-param-reassign */
                input.disabled = true;
            });
            return;
        }

        // listen to attribute changes in patient selection div
        // when it has class .has-items, an existing patient is currently selected
        // there is probably some better way to listen to this, but idk how to get the tomselect ref...
        const classObserver = new MutationObserver((mutations) => {
            mutations.forEach((mu) => {
                if (mu.type !== "attributes" && mu.attributeName !== "class") {
                    return;
                }
                const existingInputFilled = patientSelectDiv.classList.contains("has-items");
                // disable editing of the new patient inputs
                newPatientInputs.forEach((input) => {
                    /* eslint-disable-next-line no-param-reassign */
                    input.disabled = existingInputFilled;
                });

                // TODO: fetch patient's data and fill out fields in new patient form
                // or somehow get the reference to the tomselect instance
            });
        });

        classObserver.observe(patientSelectDiv, { attributes: true });

        // when observer was created, don't need change listener anymore
        existingPatientSelect.removeEventListener("change", initialPatientSelection);
    };

    // listen to first patient selection from user and update event callbacks
    if (existingPatientSelect) {
        existingPatientSelect.addEventListener("change", initialPatientSelection);
    }

    // Handle hiding and disabling fields in respective intake mode
    const intakeModeSwitch = <HTMLInputElement>document.querySelector("#intake-mode-switch");
    intakeModeSwitch.addEventListener("change", () => {
        const inEmergencyMode = intakeModeSwitch.checked;

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
            input.disabled = inEmergencyMode;
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
    const patientSearch = document.querySelector("#id_patient");
    const urlParams = new URLSearchParams(window.location.href);
    if (urlParams.get("patient") && patientSearch) {
        patientSearch.dispatchEvent(new Event("change"));
        // TODO: toggle new patient fields to readonly
    }
});
