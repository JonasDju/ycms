const addEditRemovalEventListeners = (container: HTMLElement) => {
    container.querySelectorAll<HTMLElement>(".edit-bed-remover").forEach((remover) => {
        remover.addEventListener("click", () => {
            const bed = remover.closest(".flex.items-center.gap-2");
            if (bed) {
                bed.remove();
            }
        });
    });

    container.querySelectorAll<HTMLElement>(".edit-room-remover").forEach((remover) => {
        remover.addEventListener("click", () => {
            const room = remover.closest(".edit-room");
            if (room) {
                room.remove();
            }
        });
    });
};

const newEditBedListener = (room: HTMLElement, newBedPrototype: HTMLElement) => {
    const newBedButton = room.querySelector(".edit-bed-adder") as HTMLElement;
    newBedButton.addEventListener("click", () => {
        const newBed = newBedPrototype.cloneNode(true) as HTMLElement;
        newBed.classList.remove("hidden");
        newBedButton.parentNode?.insertBefore(newBed, newBedButton);
        addEditRemovalEventListeners(room);
    });
};

const gatherRoomData2 = (): string => {
    const newRooms: Record<string, string[]> = {};
    const newRoomDivs = document.querySelectorAll(".edit-room:not(.edit-room-prototype)");

    newRoomDivs.forEach((newRoomDiv) => {
        const roomNumberInput = newRoomDiv.querySelector<HTMLInputElement>("input");
        const roomNumber = roomNumberInput?.value;

        if (!roomNumber) {
            return;
        }

        const selectValues: string[] = [];
        const selectElements = newRoomDiv.querySelectorAll<HTMLSelectElement>("select");
        selectElements.forEach((selectElement: HTMLSelectElement) => {
            if (selectElement.value) {
                selectValues.push(selectElement.value);
            }
        });

        if (selectValues.length > 0) {
            newRooms[roomNumber] = selectValues;
        }
    });

    return JSON.stringify(newRooms);
};

window.addEventListener("load", () => {
    const newRoomPrototype = document.querySelector(".edit-room-prototype")?.cloneNode(true) as HTMLElement;
    const newBedPrototype = document.querySelector(".edit-bed-prototype")?.cloneNode(true) as HTMLSelectElement;
    const editRoomDivs = document.querySelectorAll<HTMLDivElement>("[data-ward-id]");

    editRoomDivs.forEach((div) => {
        const wardId = div.getAttribute("data-ward-id")?.split("-").pop();
        const wardForm = document.querySelector(`#ward_form_${wardId}`) as HTMLFormElement;
        const newRoomButton = document.querySelector(`[data-ward-id='new-edit-room-button-${wardId}']`) as HTMLButtonElement;

        if (!newRoomPrototype || !newBedPrototype || !newRoomButton || !wardForm) {
            return;
        }

        let counter = 1;
        newRoomPrototype.classList.remove("hidden", "edit-room-prototype");

        newRoomButton.addEventListener("click", () => {
            const newRoom = newRoomPrototype.cloneNode(true) as HTMLElement;
            (newRoom.querySelector("input") as HTMLInputElement).value = `R-${counter}`;
            counter += 1;

            newRoomButton.parentNode?.insertBefore(newRoom, newRoomButton);
            newEditBedListener(newRoom, newBedPrototype);
            addEditRemovalEventListeners(newRoom);
        });

        wardForm.addEventListener("submit", (event) => {
            event.preventDefault();
            const roomData = gatherRoomData2();
            const roomsInput = window.document.querySelector(`#rooms_${wardId}`) as HTMLInputElement;
            roomsInput.value = roomData;
            wardForm.submit();
    });
    });
});
