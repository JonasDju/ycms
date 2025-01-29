const addEditRemovalEventListeners3 = (container: HTMLElement) => {
    container.querySelectorAll<HTMLElement>(".remove-bed").forEach((remover) => {
        remover.addEventListener("click", () => {
            const bed = remover.closest(".flex.items-center.gap-2");
            if (bed) {
                bed.remove();
            }
        });
    });

    container.querySelectorAll<HTMLElement>(".remover-room").forEach((remover) => {
        remover.addEventListener("click", () => {
            const room = remover.closest(".edit-room2");
            if (room) {
                room.remove();
            }
        });
    });
};

const newEditBedListener3 = (room: HTMLElement, newBedPrototype2: HTMLElement) => {
    const newBedButton = room.querySelector(".add-bed-btn") as HTMLElement;
    newBedButton.addEventListener("click", () => {
        const newBed = newBedPrototype2.cloneNode(true) as HTMLElement;
        newBed.classList.remove("hidden");
        newBedButton.parentNode?.insertBefore(newBed, newBedButton);
        addEditRemovalEventListeners3(room);
    });
};

const gatherRoomData3 = (): string => {
    const newRooms: Record<string, string[]> = {};
    const newRoomDivs = document.querySelectorAll(".edit-room2:not(.edit-room-prototype2)");

    newRoomDivs.forEach((newRoomDiv) => {
        const roomNumberInput = newRoomDiv.querySelector<HTMLInputElement>("input");
        if (roomNumberInput) {
            const roomNumber = roomNumberInput.value;
            const beds: string[] = [];
            newRoomDiv.querySelectorAll<HTMLSelectElement>("select").forEach((select) => {
                beds.push(select.value);
            });
            newRooms[roomNumber] = beds;
        }
    });

    return JSON.stringify(newRooms);
};

document.addEventListener("DOMContentLoaded", () => {
    const newRoomPrototype = document.querySelector(".edit-room-prototype2")?.cloneNode(true) as HTMLElement;
    const newBedPrototype = document.querySelector(".edit-bed-prototype2")?.cloneNode(true) as HTMLElement;
    const newRoomButton = document.querySelector("#newroom-button") as HTMLElement;
    const wardForm = document.querySelector("#ward_form") as HTMLFormElement;

    if (!newRoomPrototype || !newBedPrototype || !newRoomButton || !wardForm) {
        console.error("Required elements not found. Ensure the DOM structure is correct.");
        return;
    }

    let counter = 1;
    newRoomPrototype.classList.remove("hidden", "edit-room-prototype2");

    // Bind event listeners to the prototype elements
    addEditRemovalEventListeners3(newRoomPrototype);
    newEditBedListener3(newRoomPrototype, newBedPrototype);

    newRoomButton.addEventListener("click", () => {
        const newRoom = newRoomPrototype.cloneNode(true) as HTMLElement;
        const roomInput = newRoom.querySelector("input") as HTMLInputElement;
        if (roomInput) {
            roomInput.value = `R-${counter}`;
        }
        counter += 1;

        newRoomButton.parentNode?.insertBefore(newRoom, newRoomButton);
        newEditBedListener3(newRoom, newBedPrototype);
        addEditRemovalEventListeners3(newRoom);
    });

    wardForm.addEventListener("submit", (event) => {
        event.preventDefault();
        const roomDataInput = wardForm.querySelector(`#rooms_${wardForm.dataset.wardId}`) as HTMLInputElement;
        if (roomDataInput) {
            roomDataInput.value = gatherRoomData3();
        }
        wardForm.submit();
    });
});

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-delete-ward]").forEach((deleteButton) => {
        deleteButton.addEventListener("click", (event) => {
            event.preventDefault();

            const wardId = deleteButton.getAttribute("data-ward-id") || "";
            const formId = deleteButton.getAttribute("data-form-id") || "";
            const form = document.getElementById(formId) as HTMLFormElement;

            const modal = document.getElementById(`confirm-modal-${wardId}`);
            const confirmButton = document.querySelector(`.modal-confirm[data-ward-id='${wardId}']`);
            const cancelButton = document.querySelector(`.modal-cancel[data-ward-id='${wardId}']`);

            if (!modal || !confirmButton || !cancelButton || !form) {
                console.error("can't found", { modal, confirmButton, cancelButton, form });
                return;
            }

            modal.classList.remove("hidden");

            confirmButton.addEventListener("click", () => {
                form.submit();
                modal.classList.add("hidden");
            });

            cancelButton.addEventListener("click", () => {
                modal.classList.add("hidden");
            });
        });
    });
});
