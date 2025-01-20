const addRemovalEventListeners = (container: HTMLElement) => {
    container.querySelectorAll<HTMLElement>(".bed-remover").forEach((remover) => {
        remover.addEventListener("click", () => {
            const bed = remover.closest(".flex.items-center.gap-2");
            if (bed) {
                bed.remove();
            }
        });
    });

    container.querySelectorAll<HTMLElement>(".room-remover").forEach((remover) => {
        remover.addEventListener("click", () => {
            const room = remover.closest(".new-room");
            if (room) {
                room.remove();
            }
        });
    });
};

const newBedListener = (room: HTMLElement, newBedPrototype: HTMLElement) => {
    const newBedButton = room.querySelector(".bed-adder") as HTMLElement;
    newBedButton.addEventListener("click", () => {
        const newBed = newBedPrototype.cloneNode(true) as HTMLElement;
        newBed.classList.remove("hidden");
        newBedButton.parentNode?.insertBefore(newBed, newBedButton);
        addRemovalEventListeners(room);
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
});
