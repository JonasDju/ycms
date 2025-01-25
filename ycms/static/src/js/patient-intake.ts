window.addEventListener("load", () => {

    let weekdayNamesLong: string[] = [];

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

    const getDayOfWeek = (date: Date) =>
        // JS Date starts at Sunday=0, but need Monday=0
        /* eslint-disable-next-line no-magic-numbers */
        (((date.getDay() - 1) % 7) + 7) % 7;
    
    
    const getDateString = (date: Date) => {
        // Format the discharge date as "YYYY-MM-DD HH:MM"
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, "0");
        const day = String(date.getDate()).padStart(2, "0");
        const hours = String(date.getHours()).padStart(2, "0");
        const minutes = String(date.getMinutes()).padStart(2, "0");

        return `${year}-${month}-${day}T${hours}:${minutes}`;
    };

    function getForm(el: HTMLElement): HTMLFormElement {
        return el.closest("form") as HTMLFormElement;
    }

    function getFormAdmissionInput(form: HTMLFormElement): HTMLInputElement {
        return form.querySelector("#id_admission_date") as HTMLInputElement;
    }

    function getFormDischargeInput(form: HTMLFormElement): HTMLInputElement {
        return form.querySelector("#id_discharge_date") as HTMLInputElement;
    }

    function getFormDurationInput(form: HTMLFormElement): HTMLInputElement | null {
        return form.querySelector("#input-patient-intake-stay-duration");
    }

    function getFormWardDischargeInfo(form: HTMLFormElement): HTMLDivElement {
        return form.querySelector("#ward-discharge-days-info") as HTMLDivElement;
    }

    function getFormDischargeDateInfo(form: HTMLFormElement): HTMLDivElement {
        return form.querySelector("#discharge-date-validity") as HTMLDivElement;
    }

    function getFormMoveDischargeBtn(form: HTMLFormElement): HTMLButtonElement {
        return form.querySelector("#discharge-move-btn") as HTMLButtonElement;
    }

    // Handles the response to the fetch request for the ward's discharge policy
    // Updates the info text and stores the policy mask and localized weekday names
    /* eslint-disable-next-line @typescript-eslint/no-explicit-any */
    function setWardDischargeInfo(form: HTMLFormElement, json: any): void {
        // assumes patient intake view where ward info is fetched 
        const wardDischargeInfoDiv = getFormWardDischargeInfo(form);
        const infoTextSpan = wardDischargeInfoDiv.querySelector("span") as HTMLSpanElement;

        if (Object.keys(json).length === 0 || !json.hasOwnProperty("allowed_weekdays_short")) {
            wardDischargeInfoDiv.classList.add("hidden");
            return;
        }

        wardDischargeInfoDiv.classList.remove("hidden");

        // store localized weekday names to be used in info boxes below discharge date
        weekdayNamesLong = json.weekdays_long;

        // store ward metadata for validation
        wardDischargeInfoDiv.dataset.mask = json.mask;
        wardDischargeInfoDiv.dataset.wardName = json.name;

        const days: string[] = json.allowed_weekdays_short;
        const numAllowedDays = days.length;
        const wardName = json.name;

        if (numAllowedDays === 0) {
            infoTextSpan.textContent = formatString(
                infoTextSpan.dataset.statusNone || "'No days' status missing.",
                [wardName]
            );
            wardDischargeInfoDiv.classList.remove(...wardDischargeInfoDiv.dataset.styleValid?.split(" ") || "")
            wardDischargeInfoDiv.classList.add(...wardDischargeInfoDiv.dataset.styleInvalid?.split(" ") || "")
        } else {
            const lastDay = days.pop();
            if (days.length > 0) {
                infoTextSpan.textContent = formatString(
                    infoTextSpan.dataset.statusMulti || "'Multi day' status missing",
                    [wardName, days.join(", "), lastDay]
                );
            } else {
                infoTextSpan.textContent = formatString(
                    infoTextSpan.dataset.statusSingle || "'Single day' status missing",
                    [wardName, lastDay]
                );
            }

            wardDischargeInfoDiv.classList.remove(...wardDischargeInfoDiv.dataset.styleInvalid?.split(" ") || "")
            wardDischargeInfoDiv.classList.add(...wardDischargeInfoDiv.dataset.styleValid?.split(" ") || "")
        }
    };

    function isDischargeAfterAdmission(form: HTMLFormElement): boolean {
        const admissionDateInput = getFormAdmissionInput(form);
        const dischargeDateInput = getFormDischargeInput(form);

        if (!admissionDateInput.value || !dischargeDateInput.value) {
            return true;
        }
        
        return getNightsBetweenAdmissionAndDischarge(
            new Date(admissionDateInput.value),
            new Date(dischargeDateInput.value)
        ) >= 0;
    }

    function isDischargeDayValid(form: HTMLFormElement, date: Date): boolean {
        const wardDischargeInfo = getFormWardDischargeInfo(form);

        // if no mask is set (no ward set), default to valid
        if (!wardDischargeInfo.dataset.mask) {
            return true;
        }

        const dayOfWeek = getDayOfWeek(date);
        const mask = Number(wardDischargeInfo.dataset.mask);
        /* eslint-disable-next-line no-bitwise */
        return !!((mask >> dayOfWeek) & 0b1);
    }

    /**
     * Calculates the number of nights between an admission and discharge date.
     * Counts partial nights (e.g. from 8pm to 4am) as one night.
     * @param admission The patient admission date.
     * @param discharge The patient discharge date.
     * @returns The number of nights.
     */
    function getNightsBetweenAdmissionAndDischarge(admission: Date, discharge: Date): number {
        // const admissionDate = new Date(admissionDateInput.value);
        // const dischargeDate = new Date(dischargeDateInput.value);
        let timeDifference = discharge.getTime() - admission.getTime();
        if (timeDifference < 0) {
            return -1; // Invalid! admission lies before discharge!
        }
        // ensure that e.g. 12h over night count as one night
        /* eslint-disable no-magic-numbers */
        timeDifference = timeDifference + admission.getHours() * 3600000 + admission.getMinutes() * 60000;
        return Math.floor(timeDifference / (1000 * 3600 * 24));
        /* eslint-enable no-magic-numbers */
    };

    /**
     * Calculates the offset (in days), when the next discharge is possible in the ward as per the ward's allowed discharge days. 
     * @param form The form in which where the ward's discharge policy is defined.
     * @param date The starting date from where to get the offet.
     * @returns The offset in days to the next available discharge date or null if none exists.
     */
    function getNextValidDischargeDateOffset(form: HTMLFormElement, date: Date): number | null {
        const nextDate = new Date(date);
        /* eslint-disable no-magic-numbers */
        for (let i = 1; i < 7; i++) {
            nextDate.setDate(date.getDate() + i);
            if (isDischargeDayValid(form, nextDate)) {
                return i;
            }
        }
        /* eslint-enable no-magic-numbers */

        return null;
    };

    /**
     * Validates the current admission and discharge date inputs with the ward's policy.
     * Shows an alert box if the discharge is before the admission or the discharge 
     * is not allowed on that date in the respective ward.
     * @param form 
     */
    function validateDischargePolicy(form: HTMLFormElement): void {
        const dischargeDateInput = getFormDischargeInput(form);
        const wardName = getFormWardDischargeInfo(form).dataset.wardName;
        
        const validityInfoDiv = getFormDischargeDateInfo(form);
        const validityText = validityInfoDiv.querySelector("span[id=status]") as HTMLSpanElement;
        const nextValidText = validityInfoDiv.querySelector("div[id=next]") as HTMLDivElement;
        
        const moveDischargeBtn = getFormMoveDischargeBtn(form);
        
        // disable elements that are not used in all cases, will be enabled on demand
        nextValidText.classList.add("hidden");
        moveDischargeBtn.classList.add("hidden");
        
        const dischargeDate = new Date(dischargeDateInput.value);

        if (!isDischargeAfterAdmission(form)) {
            validityInfoDiv.classList.remove("hidden");

            // update info box
            const alert = validityInfoDiv.dataset.alertTooEarly || "Alert 'too early' missing";
            validityText.textContent = alert;

            // set custom validity to forbid user submitting the form
            dischargeDateInput.setCustomValidity(alert);
        } else if (dischargeDateInput.value && !isDischargeDayValid(form, dischargeDate)) {
            validityInfoDiv.classList.remove("hidden");
            
            // update info box
            const alert = formatString(
                validityInfoDiv.dataset.alertDayForbidden || "Alert 'forbidden day' missing",
                [wardName, weekdayNamesLong[getDayOfWeek(dischargeDate)]]
            );
            validityText.textContent = alert;
            
            // set custom validity to forbid user submitting the form
            dischargeDateInput.setCustomValidity(alert);

            // fetch next available day
            const nextValidDateOffset = getNextValidDischargeDateOffset(form, dischargeDate);
            nextValidText.classList.remove("hidden");

            if (nextValidDateOffset) {
                // push date forward to get next available
                dischargeDate.setDate(dischargeDate.getDate() + nextValidDateOffset);

                // update second line of discharge info, informing of next date
                nextValidText.textContent = formatString(
                    validityInfoDiv.dataset.dateNextAvailable || "Info 'next date' missing",
                    [wardName, dischargeDate.toLocaleDateString()]
                );

                // update move discharge button text
                moveDischargeBtn.classList.remove("hidden");
                moveDischargeBtn.textContent = formatString(
                    moveDischargeBtn.dataset.moveDischarge || "'Move discharge' text missing",
                    [dischargeDate.toLocaleDateString()]
                );
            } else {
                nextValidText.textContent = formatString(
                    validityInfoDiv.dataset.dateNoNext || "Info 'no next date' missing",
                    [wardName]
                );
            }
        } else {
            validityInfoDiv.classList.add("hidden");
            dischargeDateInput.setCustomValidity("");
        }
    };

    // Update the discharge date through formatted string, circumventing annoying UTC behavior
    function setDischargeDate(form: HTMLFormElement, date: Date): void {
        getFormDischargeInput(form).value = getDateString(date);
        validateDischargePolicy(form);
    };

    // Update the discharge date input to a set number of days after admission
    function setDischargeDateByOffset(form: HTMLFormElement, daysAfterAdmission: number): void {
        const admissionDate = new Date(getFormAdmissionInput(form).value);
        const dischargeDate = new Date(admissionDate);
        dischargeDate.setDate(admissionDate.getDate() + daysAfterAdmission);

        setDischargeDate(form, dischargeDate);
    };

    /**
     * Sets the form's discharge date widget min value s.t. user can only select dates on/after the admission.
     * @param form The form for which to update the discharge widget.
     */
    function updateDischargeMin(form: HTMLFormElement): void {
        const admissionInput = getFormAdmissionInput(form);
        const dischargeInput = getFormDischargeInput(form);

        if (admissionInput.value) {
            // set min to start of admission day (without time) so date picker widget shows day as valid
            const admissionDate = new Date(admissionInput.value);
            admissionDate.setHours(0, 0, 0, 0);
            dischargeInput.min = getDateString(admissionDate);
        } else {
            dischargeInput.min = "";
        }
    }

    function updateDurationField(form: HTMLFormElement): void {
        const durationInput = getFormDurationInput(form);
        if (!durationInput) {
            console.log("Form has no duration input");
            return;
        }

        const admissionInput = getFormAdmissionInput(form);
        const dischargeInput = getFormDischargeInput(form);

        const admission = admissionInput.value;
        const discharge = dischargeInput.value;

        if (admission && discharge) {
            const duration = getNightsBetweenAdmissionAndDischarge(
                new Date(admission),
                new Date(discharge)
            );

            if (duration >= 0) {
                durationInput.value = duration.toString();
            }
        }
    };

    const wardSelectionInputs = document.querySelectorAll<HTMLInputElement>("#id_recommended_ward");

    // update mask information if a new ward is selected (in intake only, see comment below)
    wardSelectionInputs.forEach(input => {
        const form = getForm(input);
        const wardDischargeInfo = getFormWardDischargeInfo(form);
        
        // if the mask attribute is set in template already, ignore the usage of recommended ward
        // this is the case in the ward view, where the validation should use the ward 
        //   that the patient is assigned a bed in, not the "recommended ward"
        if (wardDischargeInfo.dataset.fixedWard) {
            // TODO: remove
            console.log(`Form initialized with fixed ward ${wardDischargeInfo.dataset.fixedWard}`);
            fetch(`/intake/allowed-discharge-days/?q=${wardDischargeInfo.dataset.fixedWard}`)
                .then((response) => response.json())
                .then((json) => {
                    // update UI only once (and fetch weekday translations)
                    setWardDischargeInfo(form, json);
                    validateDischargePolicy(form);
                });
            return;
        }

        input.addEventListener("change", () => {
            if (!input.value) {
                // hide info text field
                wardDischargeInfo.classList.add("hidden");
                delete wardDischargeInfo.dataset.mask;

                validateDischargePolicy(form);
            } else {
                // fetch ward's allowed discharge days, display in info text
                const url = `/intake/allowed-discharge-days/?q=${encodeURIComponent(input.value)}`;

                fetch(url)
                    .then((response) => response.json())
                    .then((json) => {
                        setWardDischargeInfo(form, json);
                        validateDischargePolicy(form);
                    });
            }
        })
        // trigger once initially to update UI if a value is pre-filled
        input.dispatchEvent(new Event("change"));
    });

    const moveDischargeBtns = document.querySelectorAll<HTMLButtonElement>("#discharge-move-btn");

    moveDischargeBtns.forEach(btn => btn.addEventListener("click", () => {
        const form = getForm(btn);
        const dischargeInput = getFormDischargeInput(form);

        // get new discharge date by offsetting from current selection
        const currentSelectedDischarge = new Date(dischargeInput.value);
        const offsetToValid = getNextValidDischargeDateOffset(form, currentSelectedDischarge);

        if (offsetToValid) {
            currentSelectedDischarge.setDate(currentSelectedDischarge.getDate() + offsetToValid);
            setDischargeDate(form, currentSelectedDischarge);
            updateDurationField(form);
        }

        // revalidate (hides the info box and button if moving was successful)
        validateDischargePolicy(form);
    }));

    const dischargeInputs = document.querySelectorAll<HTMLInputElement>("#id_discharge_date");

    dischargeInputs.forEach(input => input.addEventListener("input", () => {
        const form = getForm(input);
        // remember that the user has manually modified the discharge date
        if (input.value) {
            input.dataset.manuallyChanged = "true";
        }

        // adjust duration of stay and validate
        updateDurationField(form);
        validateDischargePolicy(form);
    }));

    const admissionDateInputs = document.querySelectorAll<HTMLInputElement>("#id_admission_date");

    admissionDateInputs.forEach(input => input.addEventListener("input", () => {
        const form = getForm(input);
        const dischargeInput = getFormDischargeInput(form);
        const durationInput = getFormDurationInput(form);

        if (!input.value) {
            // possibly remove the alert that discharge is before admission
            validateDischargePolicy(form);
            return;
        }

        // if discharge was manually set by user, keep it as is, i.e. the timespan changes
        if (!dischargeInput.dataset.manuallyChanged) {
            // keep timespan between admission and discharge equal
            setDischargeDateByOffset(form, Number(durationInput?.value || "3"));
        }
        
        // set earliest possible discharge date, which will be shown in the date widget
        updateDischargeMin(form);

        // adjust duration of stay and validate
        updateDurationField(form);
        validateDischargePolicy(form);
    }));

    const durationInputs = document.querySelectorAll<HTMLInputElement>("#input-patient-intake-stay-duration");

    // Handle duration in nights input
    durationInputs.forEach(input => input.addEventListener("keypress", (event) => {
        if (!/^[0-9]$/.test(event.key)) {
            // Avoid input that is no digit
            event.preventDefault();
        }
    }));

    durationInputs.forEach(input => input.addEventListener("input", () => {
        const form = getForm(input);
        const dischargeInput = getFormDischargeInput(form);

        // Remove leading zeros
        if (input.value.startsWith("0") && input.value.length > 1) {
            input.value = input.value.replace(/^0+/, "");
        }
        if (input.value.length === 0) {
            input.value = "0";
        }
        // adjust Discharge date according to the duration in nights
        setDischargeDateByOffset(form, Number(input.value));

        // discharge date should now follow admission by offset instead of being fixed
        delete dischargeInput.dataset.manuallyChanged;
    }));

    // Buttons for setting stay duration with fixed value
    document.querySelectorAll<HTMLButtonElement>("#stay-duration-btn")
        .forEach(btn => btn.addEventListener("click", () => {
            // these buttons are in a subform
            const form = getForm(btn);
            const durationInput = getFormDurationInput(form);
            const dischargeInput = getFormDischargeInput(form);

            if (!durationInput || !btn.dataset.duration) return;

            durationInput.value = btn.dataset.duration;
            setDischargeDateByOffset(form, Number(btn.dataset.duration));
            // discharge date should now follow admission by offset instead of being fixed
            delete dischargeInput.dataset.manuallyChanged;
        }));


    const wardDischargeInfos = document.querySelectorAll<HTMLDivElement>("#ward-discharge-days-info");
    
    wardDischargeInfos.forEach(div => {
        const form = getForm(div);

        // move ward's discharge info below recommended ward if that is used to update the validation
        if (!div.dataset.fixedWard) {
            const wardSelect = form.querySelector("#id_recommended_ward") as HTMLSelectElement;
            const newParent = wardSelect.parentNode?.parentNode;
            
            if (newParent) {
                newParent.appendChild(div);
            } else {
                console.log("Could not get grandparent of #id_recommended_ward", div);
            }
        }

        updateDischargeMin(form);
        // perform one update to all forms to show alerts for initial data
        validateDischargePolicy(form);
    });
});
