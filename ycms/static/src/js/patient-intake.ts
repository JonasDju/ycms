window.addEventListener("load", () => {
    // all js/ts files are loaded on all pages, and the event listeners below will
    // throw errors since most (but not all!) of the DOM elements referenced below
    // exist in other pages as well... yeah...
    if (!window.location.toString().includes("intake")) {
        return;
    }

    // ward select and attached info box
    const wardSelectionInput = document.querySelector("#id_recommended_ward") as HTMLSelectElement;
    const wardDischargeInfoDiv = document.querySelector("#ward-discharge-info") as HTMLDivElement;
    const wardDischargeInfoText = document.querySelector("#ward-discharge-info-text") as HTMLDivElement;

    // intake/discharge date inputs
    const admissionDateInput = document.querySelector("#id_admission_date") as HTMLInputElement;
    const dischargeDateInput = document.querySelector("#id_discharge_date") as HTMLInputElement;
    const durationInput = document.querySelector("#input-patient-intake-stay-duration") as HTMLInputElement;

    const buttonTwoNights = document.querySelector("#button-patient-intake-2n") as HTMLButtonElement;
    const buttonSevenNights = document.querySelector("#button-patient-intake-7n") as HTMLButtonElement;
    const buttonFourteenNights = document.querySelector("#button-patient-intake-14n") as HTMLButtonElement;

    // discharge validity feedback elements
    const dischargeInvalidDiv = document.querySelector("#intake-info-discharge-invalid") as HTMLElement;
    const dischargeInvalidText = document.querySelector("#intake-info-discharge-invalid-text") as HTMLElement;
    const dischargeValidDiv = document.querySelector("#intake-info-discharge-valid") as HTMLElement;
    const moveDischargeDateBtn = document.querySelector("#intake-discharge-move-btn") as HTMLButtonElement;

    // TODO: move to html
    // styling
    const infoBoxBlue = ["text-blue-800", "bg-blue-50", "dark:text-blue-400"];
    const infoBoxRed = ["text-red-800", "bg-red-50", "dark:text-red-400"];

    let weekdayNamesLong = [];

    // Handles the response to the fetch request for the ward's discharge policy
    // Updates the info text and stores the policy mask and localized weekday names
    /* eslint-disable-next-line @typescript-eslint/no-explicit-any */
    const setWardDischargeInfo = (json: any) => {
        if (Object.keys(json).length === 0) {
            wardDischargeInfoDiv.classList.add("hidden");
            return;
        }

        // store localized weekday names to be used in info boxes below discharge date
        weekdayNamesLong = json.weekdays_long;

        let res = json.info_text[0];
        const numAllowedDays = json.allowed_weekdays_short.length;
        if (numAllowedDays === 0) {
            wardDischargeInfoDiv.classList.remove(...infoBoxBlue);
            wardDischargeInfoDiv.classList.add(...infoBoxRed);
        } else {
            wardDischargeInfoDiv.classList.remove(...infoBoxRed);
            wardDischargeInfoDiv.classList.add(...infoBoxBlue);

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

        wardDischargeInfoDiv.classList.remove("hidden");
        wardDischargeInfoText.textContent = res;
    };

    // Update the discharge date input to a set number of days after admission
    const setDischargeDateByOffset = (daysAfterAdmission: number) => {
        const admissionDate = new Date(admissionDateInput.value);
        const dischargeDate = new Date(admissionDate);
        dischargeDate.setDate(admissionDate.getDate() + daysAfterAdmission);
        // Format the discharge date as "YYYY-MM-DD HH:MM"
        const year = dischargeDate.getFullYear();
        const month = String(dischargeDate.getMonth() + 1).padStart(2, "0");
        const day = String(dischargeDate.getDate()).padStart(2, "0");
        const hours = String(dischargeDate.getHours()).padStart(2, "0");
        const minutes = String(dischargeDate.getMinutes()).padStart(2, "0");
        dischargeDateInput.value = `${year}-${month}-${day}T${hours}:${minutes}`;
    };

    // Gets the number of nights with the current inputs for admission and discharge
    const getNightsBetweenAdmissionAndDischarge = () => {
        const admissionDate = new Date(admissionDateInput.value);
        const dischargeDate = new Date(dischargeDateInput.value);
        let timeDifference = dischargeDate.getTime() - admissionDate.getTime();
        if (timeDifference < 0) {
            return -1; // Invalid! admission lies before discharge!
        }
        // ensure that e.g. 12h over night count as one night
        /* eslint-disable no-magic-numbers */
        timeDifference = timeDifference + admissionDate.getHours() * 3600000 + admissionDate.getMinutes() * 60000;
        return Math.floor(timeDifference / (1000 * 3600 * 24));
        /* eslint-enable no-magic-numbers */
    };

    // Gets the next date on which discharge is possible in the currently selected ward and the discharge policy mask
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

    // Validates the current value of the discharge date against the selected ward's policy
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

    wardSelectionInput?.addEventListener("change", () => {
        if (!wardSelectionInput.value) {
            // hide info text field
            wardDischargeInfoDiv.classList.add("hidden");
            dischargeInvalidText.removeAttribute("mask");
            // hide feedback for discharge validity
            dischargeInvalidDiv.classList.add("hidden");
            dischargeValidDiv.classList.add("hidden");
        } else {
            // fetch ward's allowed discharge days, display in info text
            const url = `/intake/allowed-discharge-days/?q=${encodeURIComponent(wardSelectionInput.value)}`;

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

    moveDischargeDateBtn?.addEventListener("click", () => {
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

    // TODO: update event listeners to validate discharge date
    dischargeDateInput?.addEventListener("input", () => {
        // Mark whether the user has manually modified the discharge date
        dischargeDateInput.setAttribute("data-manually-changed", "true");
        // Adjust duration of stay
        const duration = getNightsBetweenAdmissionAndDischarge();

        durationInput.value = Math.max(duration, 0).toString();
    });

    admissionDateInput?.addEventListener("input", () => {
        // Check if the discharge date has been manually modified
        const isDischargeManuallyChanged = dischargeDateInput.getAttribute("data-manually-changed") === "true";
        // Only when the discharge date is not manually modified, it is automatically set to one week after admission
        if (!isDischargeManuallyChanged) {
            /* eslint-disable-next-line no-magic-numbers */
            setDischargeDateByOffset(7);
        }
        // Adjust duration of stay
        const duration = getNightsBetweenAdmissionAndDischarge();
        durationInput.value = Math.max(duration, 0).toString();
    });

    // Avoid an admission date that lies behind a discharge date
    dischargeDateInput?.addEventListener("focusout", () => {
        if (getNightsBetweenAdmissionAndDischarge() < 0) {
            dischargeDateInput.value = admissionDateInput.value;
        }
    });
    admissionDateInput?.addEventListener("focusout", () => {
        if (getNightsBetweenAdmissionAndDischarge() < 0) {
            dischargeDateInput.value = admissionDateInput.value;
        }
    });

    // Handle duration in nights input
    durationInput?.addEventListener("keypress", (event) => {
        if (!/^[0-9]$/.test(event.key)) {
            // Avoid input that is no digit
            event.preventDefault();
        }
    });
    durationInput?.addEventListener("input", () => {
        // Remove leading zeros
        if (durationInput.value.startsWith("0") && durationInput.value.length > 1) {
            durationInput.value = durationInput.value.replace(/^0+/, "");
        }
        if (durationInput.value.length === 0) {
            durationInput.value = "0";
        }
        // Adjust Discharge date according to the duration in nights
        setDischargeDateByOffset(Number(durationInput.value));
    });

    /* eslint-disable no-magic-numbers */
    // Common stay duration buttons
    buttonTwoNights?.addEventListener("click", () => {
        durationInput.value = "2";
        setDischargeDateByOffset(2);
    });
    buttonSevenNights?.addEventListener("click", () => {
        durationInput.value = "7";
        setDischargeDateByOffset(7);
    });
    buttonFourteenNights?.addEventListener("click", () => {
        durationInput.value = "14";
        setDischargeDateByOffset(14);
    });
    /* eslint-enable no-magic-numbers */
});
