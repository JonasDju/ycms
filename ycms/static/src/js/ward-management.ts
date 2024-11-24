const addRemovalEventListeners = (room: HTMLElement) => {
    room.querySelectorAll<HTMLElement>(".element-remover").forEach((remover) => {
        remover.addEventListener("click", () => {
            (remover.parentNode?.parentNode as HTMLElement)?.remove();
        });
    });
};

const newBedListener = (room: HTMLElement, newBedPrototype: HTMLElement) => {
    const newBedButton = room.querySelector(".bed-adder") as HTMLElement;
    newBedButton.addEventListener("click", () => {
        newBedButton.parentNode?.insertBefore(newBedPrototype.cloneNode(true), newBedButton);
    });
};

const gatherRoomData = (): string => {
    const newRooms: Record<string, string[]> = {};
    const newRoomDivs = document.querySelectorAll(".new-room:not(.new-room-prototype)");

    newRoomDivs.forEach((newRoomDiv) => {
        const roomNumberInput = newRoomDiv.querySelector<HTMLInputElement>("input");
        const roomNumber = roomNumberInput?.value;

        if (!roomNumber) {
            return;
        }

        const selectValues: string[] = [];
        const selectElements = newRoomDiv.querySelectorAll<HTMLSelectElement>("select");
        selectElements.forEach((selectElement: HTMLSelectElement) => {
            selectValues.push(selectElement.value);
        });

        newRooms[roomNumber] = selectValues;
    });

    return JSON.stringify(newRooms);
};

window.addEventListener("load", () => {
    const newRoomPrototype = document.querySelector(".new-room-prototype")?.cloneNode(true) as HTMLElement;
    const newBedPrototype = document.querySelector(".new-bed-prototype")?.cloneNode(true) as HTMLSelectElement;
    const newRoomButton = document.querySelector("#new-room-button") as HTMLElement;
    const wardForm = document.querySelector("#ward_form") as HTMLFormElement;

    if (!newRoomPrototype || !newBedPrototype || !newRoomButton || !wardForm) {
        return;
    }

    let counter = 1;
    newRoomPrototype.classList.remove("hidden", "new-room-prototype");

    newRoomButton.addEventListener("click", () => {
        const newRoom = newRoomPrototype.cloneNode(true) as HTMLElement;
        (newRoom.querySelector("input") as HTMLInputElement).value = `R-${counter}`;
        counter += 1;

        newRoomButton.parentNode?.insertBefore(newRoom, newRoomButton);
        newBedListener(newRoom, newBedPrototype);
        addRemovalEventListeners(newRoom);
    });

    wardForm.addEventListener("submit", (event) => {
        event.preventDefault();
        (wardForm.querySelector("#rooms") as HTMLInputElement).value = gatherRoomData();
        wardForm.submit();
    });

    document.querySelectorAll("[data-delete-ward]").forEach((deleteButton) => {
        deleteButton.addEventListener("click", (event) => {
            event.preventDefault();
            const occupiedBeds = parseInt(deleteButton.getAttribute("data-occupied-beds") || "0", 10);
            const formId = deleteButton.getAttribute("data-form-id") || "";
            const form = document.getElementById(formId) as HTMLFormElement;

            const modal = document.getElementById("confirm-modal");
            const modalMessage = document.getElementById("modal-message");
            const confirmButton = document.getElementById("modal-confirm");
            const cancelButton = document.getElementById("modal-cancel");

            if (!modal || !modalMessage || !confirmButton || !cancelButton || !form) {
                return;
            }

            modalMessage.innerText =
                occupiedBeds > 0
                    ? `This ward has ${occupiedBeds} occupied beds. Are you sure you want to delete it?`
                    : "Are you sure you want to delete this ward?";

            modal.style.display = "flex";

            confirmButton.onclick = () => {
                form.submit();
                modal.style.display = "none";
            };

            cancelButton.onclick = () => {
                modal.style.display = "none";
            };
        });
    });
});
