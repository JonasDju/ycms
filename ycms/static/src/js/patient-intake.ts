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

    // TODO: move to html
    // styling
    const infoBoxBlue = ["text-blue-800", "bg-blue-50", "dark:text-blue-400"];
    const infoBoxRed = ["text-red-800", "bg-red-50", "dark:text-red-400"];

    let weekdayNamesLong: string[] = [];

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
        console.log(weekdayNamesLong);

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

    const clearAlerts = () => {
        dischargeInvalidDiv.classList.add("hidden");
        dischargeBeforeAdmissionDiv.classList.add("hidden");
    };

    const alertDischargeBeforeAdmission = () => {
        clearAlerts();
        dischargeBeforeAdmissionDiv.classList.remove("hidden");
    };

    const alertInvalidWeekday = (invalidDay: string, nextValidDay: string) => {
        clearAlerts();
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

    const getDayOfWeek = (date: Date) =>
        // JS Date starts at Sunday=0, but need Monday=0
        /* eslint-disable-next-line no-magic-numbers */
        (((date.getDay() - 1) % 7) + 7) % 7;

    const isValidDischargeDay = (date: Date) => {
        // if no mask is set (no ward set), default to valid
        if (!dischargeDateInput.hasAttribute("mask")) {
            console.log("no mask set");
            return true;
        }

        const dayOfWeek = getDayOfWeek(date);
        const mask = Number(dischargeDateInput.getAttribute("mask"));
        /* eslint-disable-next-line no-bitwise */
        return (mask >> dayOfWeek) & 0b1;
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
    const getNextValidDischargeDateOffset = (date: Date) => {
        console.log("getting next valid day from ", date);
        const nextDate = new Date(date);
        /* eslint-disable no-magic-numbers */
        for (let i = 1; i < 7; i++) {
            nextDate.setDate(date.getDate() + i);
            if (isValidDischargeDay(nextDate)) {
                console.log("found offset ", i, nextDate);
                return i;
            }
        }
        /* eslint-enable no-magic-numbers */

        return null;
    };

    const updateDurationField = () => {
        if (admissionDateInput.value && dischargeDateInput.value) {
            const duration = getNightsBetweenAdmissionAndDischarge();
            if (duration >= 0) {
                durationInput.value = duration.toString();
            } else {
                // TODO: clear??
                // durationInput.value = "";
            }
        }
    };

    // Validates the current value of the discharge date against the selected ward's policy
    // TODO: validation when changing discharge through number of nights input
    const validateDischargePolicy = () => {
        const dateString = dischargeDateInput.value;
        // no date entered, or no ward set
        if (!dateString || !dischargeDateInput.hasAttribute("mask") || weekdayNamesLong.length === 0) {
            // TODO: dont want to clear disch < adm alert!
            console.log("early return validate policy");
            clearAlerts();
            return;
        }

        const date = new Date(dateString);

        if (!isValidDischargeDay(date)) {
            console.log(date, "is invalid");
            // TODO: translation
            const selectedWeekday = weekdayNamesLong[getDayOfWeek(date)];
            const nextValidDateOffset = getNextValidDischargeDateOffset(date);
            if (nextValidDateOffset) {
                date.setDate(date.getDate() + nextValidDateOffset);
                alertInvalidWeekday(selectedWeekday, date.toLocaleDateString());
                // TODO: store discharge date, so wont need to be recalculated on button press
                // moveDischargeDateBtn.setAttribute("moveTo", nextPossibleDischargeDate);
            } else {
                alertInvalidWeekday(selectedWeekday, "");
            }
        } else {
            console.log(date, " is valid");
        }
    };

    wardSelectionInput?.addEventListener("change", () => {
        if (!wardSelectionInput.value) {
            // hide info text field
            wardDischargeInfoDiv.classList.add("hidden");
            dischargeDateInput.removeAttribute("mask");
            // TODO: hide feedback for discharge validity
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
                });
        }
    });

    moveDischargeDateBtn?.addEventListener("click", () => {
        const currentDate = new Date(dischargeDateInput.value);
        const mask = Number(dischargeDateInput.getAttribute("mask"));

        if (currentDate && mask) {
            // TODO: update with formatted string since .valueAsDate sets UTC date
            // TODO: fetch stored moveTo date
            const currentOffset = getNightsBetweenAdmissionAndDischarge();
            const offsetToValid = getNextValidDischargeDateOffset(currentDate);
            if (offsetToValid) {
                setDischargeDateByOffset(currentOffset + offsetToValid);
            }
            // TODO: update number of nights field
            // const durationInput = document.querySelector("#input-patient-intake-stay-duration") as HTMLInputElement;
            // durationInput.value =
            // TODO: if user changed discharge by offset (number of nights field), save this value so it will be used again when intake date changes
            // TODO: revalidate or somehow give feedback for successful moving of discharge date
            validateDischargePolicy();
        }
    });

    dischargeDateInput?.addEventListener("input", () => {
        // Mark whether the user has manually modified the discharge date
        dischargeDateInput.setAttribute("data-manually-changed", "true");

        if (!dischargeDateInput.value) {
            clearAlerts();
            return;
        }
        if (!admissionDateInput.value) {
            // no need to check if admission is after discharge
            validateDischargePolicy();
        } else {
            const duration = getNightsBetweenAdmissionAndDischarge();
            if (duration < 0) {
                alertDischargeBeforeAdmission();
                dischargeDateInput.value = "";
                durationInput.value = "";
                return;
            }
        }

        // Adjust duration of stay
        updateDurationField();
        validateDischargePolicy();
    });

    admissionDateInput?.addEventListener("input", () => {
        if (!admissionDateInput.value) {
            clearAlerts();
        } else if (dischargeDateInput.getAttribute("data-manually-changed") === "true") {
            // keep discharge at its current value if it was modified by the user
            // but check if discharge is before admission
            const duration = getNightsBetweenAdmissionAndDischarge();
            if (dischargeDateInput.value && duration < 0) {
                alertDischargeBeforeAdmission();
                dischargeDateInput.value = "";
                durationInput.value = "";
                return;
            }
        } else {
            // offset discharge with current duration input value or one week as fallback
            setDischargeDateByOffset(Number(durationInput.value || "7"));
            clearAlerts();
        }

        // Adjust duration of stay
        updateDurationField();
        validateDischargePolicy();
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
