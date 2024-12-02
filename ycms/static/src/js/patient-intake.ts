window.addEventListener("load", () => {
    // all js/ts files are loaded on all pages, and the event listeners below will
    // throw errors since most (but not all!) of the DOM elements referenced below
    // exist in other pages as well... yeah...
    if (!window.location.toString().includes("intake")) {
        return;
    }

    // ward select and attached info box
    const wardSelectionInput = document.querySelector("#id_recommended_ward") as HTMLSelectElement;

    const wardDischargeInfoDiv = document.querySelector("#ward-allowed-discharge-days-info") as HTMLDivElement;
    const wardDischargeAlertDiv = document.querySelector("#ward-no-allowed-discharge-alert") as HTMLDivElement;
    const wardDischargeAllowedDaysFirst = document.querySelector(
        "#ward-allowed-discharge-days-first",
    ) as HTMLDivElement;
    const wardDischargeAllowedDaysAnd = document.querySelector("#ward-allowed-discharge-days-and") as HTMLDivElement;
    const wardDischargeAllowedDaysLast = document.querySelector("#ward-allowed-discharge-days-last") as HTMLDivElement;

    // intake/discharge date inputs
    const admissionDateInput = document.querySelector("#id_admission_date") as HTMLInputElement;
    const dischargeDateInput = document.querySelector("#id_discharge_date") as HTMLInputElement;
    const durationInput = document.querySelector("#input-patient-intake-stay-duration") as HTMLInputElement;

    const buttonTwoNights = document.querySelector("#button-patient-intake-2n") as HTMLButtonElement;
    const buttonSevenNights = document.querySelector("#button-patient-intake-7n") as HTMLButtonElement;
    const buttonFourteenNights = document.querySelector("#button-patient-intake-14n") as HTMLButtonElement;

    // discharge validity feedback elements
    const dischargeInvalidDiv = document.querySelector("#intake-alert-discharge-invalid") as HTMLDivElement;
    const dischargeInvalidDayText = document.querySelector("#intake-alert-discharge-invalid-day") as HTMLSpanElement;
    const dischargeInvalidWithNextDiv = document.querySelector(
        "#intake-alert-discharge-with-next-day",
    ) as HTMLDivElement;
    const dischargeInvalidNextDayText = document.querySelector("#intake-alert-discharge-next-day") as HTMLSpanElement;
    const dischargeInvalidNoNextDayDiv = document.querySelector(
        "#intake-alert-discharge-no-next-day",
    ) as HTMLDivElement;

    const moveDischargeDateBtn = document.querySelector("#intake-discharge-move-btn") as HTMLButtonElement;
    const moveDischargeDateText = document.querySelector("#intake-discharge-move-day") as HTMLSpanElement;

    const dischargeBeforeAdmissionDiv = document.querySelector(
        "#intake-alert-discharge-before-admission",
    ) as HTMLDivElement;

    let weekdayNamesLong: string[] = [];

    // Handles the response to the fetch request for the ward's discharge policy
    // Updates the info text and stores the policy mask and localized weekday names
    /* eslint-disable-next-line @typescript-eslint/no-explicit-any */
    const setWardDischargeInfo = (json: any) => {
        if (Object.keys(json).length === 0) {
            wardDischargeInfoDiv.classList.add("hidden");
            wardDischargeAlertDiv.classList.add("hidden");
            return;
        }

        // store localized weekday names to be used in info boxes below discharge date
        weekdayNamesLong = json.weekdays_long;

        const numAllowedDays = json.allowed_weekdays_short.length;
        if (numAllowedDays === 0) {
            wardDischargeInfoDiv.classList.add("hidden");
            wardDischargeAlertDiv.classList.remove("hidden");
            return;
        }

        wardDischargeInfoDiv.classList.remove("hidden");
        wardDischargeAlertDiv.classList.add("hidden");

        let firstDays = "";
        const lastDay = ` ${json.allowed_weekdays_short[numAllowedDays - 1]}`;

        if (numAllowedDays > 1) {
            json.allowed_weekdays_short.slice(0, numAllowedDays - 2).forEach((day: string) => {
                firstDays += `${day}, `;
            });
            firstDays += json.allowed_weekdays_short[numAllowedDays - 2];
        }

        if (firstDays) {
            wardDischargeAllowedDaysFirst.textContent = ` ${firstDays} `;
            wardDischargeAllowedDaysFirst.classList.remove("hidden");
            wardDischargeAllowedDaysAnd.classList.remove("hidden");
        } else {
            wardDischargeAllowedDaysFirst.classList.add("hidden");
            wardDischargeAllowedDaysAnd.classList.add("hidden");
        }

        wardDischargeAllowedDaysLast.textContent = lastDay;
    };

    const clearDischargeBeforeAdmissionAlert = () => {
        dischargeBeforeAdmissionDiv.classList.add("hidden");
    };

    const clearWeekdayAlert = () => {
        dischargeInvalidDiv.classList.add("hidden");
    };

    const alertDischargeBeforeAdmission = () => {
        clearWeekdayAlert();
        dischargeBeforeAdmissionDiv.classList.remove("hidden");
    };

    const alertInvalidWeekday = (invalidDay: string, nextValidDay: string) => {
        clearDischargeBeforeAdmissionAlert();
        dischargeInvalidDiv.classList.remove("hidden");
        dischargeInvalidDayText.textContent = invalidDay;
        if (nextValidDay) {
            dischargeInvalidNoNextDayDiv.classList.add("hidden");

            dischargeInvalidWithNextDiv.classList.remove("hidden");
            dischargeInvalidNextDayText.textContent = nextValidDay;

            moveDischargeDateBtn.classList.remove("hidden");
            moveDischargeDateText.textContent = nextValidDay;
        } else {
            dischargeInvalidWithNextDiv.classList.add("hidden");
            dischargeInvalidNoNextDayDiv.classList.remove("hidden");
            moveDischargeDateBtn.classList.add("hidden");
        }
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

    const getDayOfWeek = (date: Date) =>
        // JS Date starts at Sunday=0, but need Monday=0
        /* eslint-disable-next-line no-magic-numbers */
        (((date.getDay() - 1) % 7) + 7) % 7;

    const isValidDischargeDay = (date: Date) => {
        // if no mask is set (no ward set), default to valid
        if (!dischargeDateInput.hasAttribute("mask")) {
            return true;
        }

        const dayOfWeek = getDayOfWeek(date);
        const mask = Number(dischargeDateInput.getAttribute("mask"));
        /* eslint-disable-next-line no-bitwise */
        return (mask >> dayOfWeek) & 0b1;
    };

    // Gets the next date on which discharge is possible in the currently selected ward and the discharge policy mask
    const getNextValidDischargeDateOffset = (date: Date) => {
        const nextDate = new Date(date);
        /* eslint-disable no-magic-numbers */
        for (let i = 1; i < 7; i++) {
            nextDate.setDate(date.getDate() + i);
            if (isValidDischargeDay(nextDate)) {
                return i;
            }
        }
        /* eslint-enable no-magic-numbers */

        return null;
    };

    const validateDischargeAfterAdmission = () => {
        if (admissionDateInput.value && dischargeDateInput.value) {
            const duration = getNightsBetweenAdmissionAndDischarge();

            if (duration < 0) {
                alertDischargeBeforeAdmission();
                dischargeDateInput.value = "";
                durationInput.value = "";
                return;
            }
        }

        clearDischargeBeforeAdmissionAlert();
    };

    // Validates the current value of the discharge date against the selected ward's policy
    const validateDischargePolicy = () => {
        // no date entered, or no ward set
        if (!dischargeDateInput.value || !dischargeDateInput.hasAttribute("mask") || weekdayNamesLong.length === 0) {
            clearWeekdayAlert();
            return;
        }

        const date = new Date(dischargeDateInput.value);

        if (!isValidDischargeDay(date)) {
            const selectedWeekday = weekdayNamesLong[getDayOfWeek(date)];
            const nextValidDateOffset = getNextValidDischargeDateOffset(date);
            if (nextValidDateOffset) {
                date.setDate(date.getDate() + nextValidDateOffset);
                alertInvalidWeekday(selectedWeekday, date.toLocaleDateString());
            } else {
                alertInvalidWeekday(selectedWeekday, "");
            }
        } else {
            clearWeekdayAlert();
        }
    };

    const getDateString = (date: Date) => {
        // Format the discharge date as "YYYY-MM-DD HH:MM"
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, "0");
        const day = String(date.getDate()).padStart(2, "0");
        const hours = String(date.getHours()).padStart(2, "0");
        const minutes = String(date.getMinutes()).padStart(2, "0");

        return `${year}-${month}-${day}T${hours}:${minutes}`;
    };

    // Update the discharge date through formatted string, circumventing annoying UTC behavior
    const setDischargeDate = (date: Date) => {
        dischargeDateInput.value = getDateString(date);

        // admission alert takes precedence
        validateDischargePolicy();
        validateDischargeAfterAdmission();
    };

    // Update the discharge date input to a set number of days after admission
    const setDischargeDateByOffset = (daysAfterAdmission: number) => {
        const admissionDate = new Date(admissionDateInput.value);
        const dischargeDate = new Date(admissionDate);
        dischargeDate.setDate(admissionDate.getDate() + daysAfterAdmission);

        setDischargeDate(dischargeDate);
    };

    const updateDurationField = () => {
        if (admissionDateInput.value && dischargeDateInput.value) {
            const duration = getNightsBetweenAdmissionAndDischarge();
            if (duration >= 0) {
                durationInput.value = duration.toString();
            }
        }
    };

    wardSelectionInput?.addEventListener("change", () => {
        if (!wardSelectionInput.value) {
            // hide info text field
            wardDischargeInfoDiv.classList.add("hidden");
            dischargeDateInput.removeAttribute("mask");
            clearWeekdayAlert();
        } else {
            // fetch ward's allowed discharge days, display in info text
            const url = `/intake/allowed-discharge-days/?q=${encodeURIComponent(wardSelectionInput.value)}`;

            fetch(url)
                .then((response) => response.json())
                .then((json) => {
                    setWardDischargeInfo(json);
                    // store mask for validation
                    dischargeDateInput.setAttribute("mask", json.mask);
                    validateDischargePolicy();
                    // recheck that discharge is after admission, this alert takes precedence
                    validateDischargeAfterAdmission();
                });
        }
    });

    moveDischargeDateBtn?.addEventListener("click", () => {
        // remove alert on button press
        clearWeekdayAlert();

        if (!dischargeDateInput.value) {
            return;
        }

        // get new discharge date by offsetting from current selection
        const currentSelectedDischarge = new Date(dischargeDateInput.value);
        const offsetToValid = getNextValidDischargeDateOffset(currentSelectedDischarge);

        if (offsetToValid) {
            currentSelectedDischarge.setDate(currentSelectedDischarge.getDate() + offsetToValid);
            setDischargeDate(currentSelectedDischarge);
            updateDurationField();
        } else {
            // reenable alert if we somehow cannot find a next date
            validateDischargePolicy();
        }
    });

    dischargeDateInput?.addEventListener("input", () => {
        // Mark whether the user has manually modified the discharge date
        dischargeDateInput.setAttribute("data-manually-changed", "true");

        // if no discharge is given, need no alerts :)
        if (!dischargeDateInput.value) {
            clearWeekdayAlert();
            clearDischargeBeforeAdmissionAlert();
            return;
        }

        // Adjust duration of stay
        updateDurationField();
        validateDischargePolicy();
        validateDischargeAfterAdmission();
    });

    admissionDateInput?.addEventListener("input", () => {
        if (!admissionDateInput.value) {
            clearDischargeBeforeAdmissionAlert();
        } else if (dischargeDateInput.getAttribute("data-manually-changed") === "true") {
            // keep discharge at its current value if it was modified by the user
            // but check if discharge is before admission
            validateDischargeAfterAdmission();
        } else {
            // offset discharge with current duration input value or one week as fallback
            clearDischargeBeforeAdmissionAlert();
            setDischargeDateByOffset(Number(durationInput.value || "7"));
        }

        if (admissionDateInput.value) {
            dischargeDateInput.min = getDateString(new Date(admissionDateInput.value));
        } else {
            dischargeDateInput.min = "";
        }

        // Adjust duration of stay
        updateDurationField();
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

        // discharge date should now follow admission by offset instead of being fixed
        dischargeDateInput.setAttribute("data-manually-changed", "false");
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

    // set initial min value for discharge (should be today)
    if (admissionDateInput.value) {
        dischargeDateInput.min = getDateString(new Date(admissionDateInput.value));
    }
});
