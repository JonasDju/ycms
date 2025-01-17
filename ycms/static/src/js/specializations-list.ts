// switch between fixed values and input fields, also switch edit/del <-> cancel/save
const editSpecialization = (id: string) => {
    const row = document.querySelector(`[data-specialization-id='${id}']`);
    if (row != null) {
        for (const column of row.children) {
            for (const child of column.children) {
                child.classList.toggle("!hidden");
            }
        }
    }
};

window.addEventListener("load", () => {
    const editSpecButtons = document.querySelectorAll(".edit-specialization-button");
    editSpecButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const id = button.parentElement?.parentElement?.parentElement?.getAttribute("data-specialization-id") as string;
            editSpecialization(id);
        });
    });
});
