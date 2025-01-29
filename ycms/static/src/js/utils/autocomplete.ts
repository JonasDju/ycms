import TomSelect from "tom-select";

const newTomSelect = (element: string, endpoint: string) => {
    const domElement = document.querySelector(element) as HTMLSelectElement;
    if (!domElement) {
        return;
    }
    const isDisabled = domElement.hasAttribute("disabled");
    /* eslint-disable-next-line no-new */
    const tomSelect = new TomSelect(element, {
        valueField: "id",
        labelField: "name",
        searchField: ["id", "name"],
        selectOnTab: true,
        items: [...domElement.options].map((el) => el.value),
        /* eslint-disable-next-line @typescript-eslint/no-explicit-any */
        load: (query: string, callback: any) => {
            // tomselect element may be disabled when user has no permissions to use it
            if (isDisabled) {
                callback([]);
                return;
            }

            const url = `/autocomplete/${endpoint}/?q=${encodeURIComponent(query)}`;
            fetch(url)
                .then((response) => response.json())
                .then((json) => {
                    callback(json.suggestions);
                });
        },
    });

    if (isDisabled) {
        tomSelect.disable();
    }
};

window.addEventListener("load", () => {
    const diagnosisInputs = document.querySelectorAll<HTMLInputElement>(".async_diagnosis_code");
    const autosuggestionConfig = [["#id_patient", "patient"]];
    diagnosisInputs.forEach((input) => {
        autosuggestionConfig.push([`#${input.id}`, "icd10"]);
    });
    autosuggestionConfig.forEach((element) => {
        newTomSelect(element[0], element[1]);
    });
});
