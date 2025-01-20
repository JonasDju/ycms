const editPatient = (id: string) => {
    const row = document.querySelector(`[data-patient-id='${id}']`);
    if (row != null) {
        for (const column of row.children) {
            for (const child of column.children) {
                child.classList.toggle("!hidden");
            }
        }
    }
};

const searchPatients = (name: string) => {
    const form = document.getElementById("search-patient-form") as HTMLFormElement;
    form.submit();
};

window.addEventListener("load", () => {
    const editPatientButtons = document.querySelectorAll(".edit-patient-button");
    editPatientButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const id = button.parentElement?.parentElement?.parentElement?.getAttribute("data-patient-id") as string;
            editPatient(id);
        });
    });

    const searchPatientInput = document.querySelector("#search-patient-input") as HTMLInputElement;
    if (!searchPatientInput) {
        return;
    }
    searchPatientInput.addEventListener("change", () => {
        const name = searchPatientInput.value;
        searchPatients(name);
    });
});
