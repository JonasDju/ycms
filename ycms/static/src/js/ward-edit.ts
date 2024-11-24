const addRemovalEventListeners2 = (room: HTMLElement) => {
    room.querySelectorAll<HTMLElement>(".element-remover").forEach((remover) => {
        remover.addEventListener("click", () => {
            (remover.parentNode?.parentNode as HTMLElement)?.remove();
        });
    });
};

const newBedListener2 = (room: HTMLElement, newBedPrototype: HTMLElement) => {
    const newBedButton = room.querySelector(".bed-adder") as HTMLElement;
    newBedButton.addEventListener("click", () => {
        newBedButton.parentNode?.insertBefore(newBedPrototype.cloneNode(true), newBedButton);
    });
};

const gatherRoomData2 = (): string => {
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
    const wardForm = document.querySelector("#ward_form") as HTMLFormElement;
    const editRoomDivs = document.querySelectorAll<HTMLDivElement>("[data-ward-id]");
    
    editRoomDivs.forEach((div) => {
        const id = div.getAttribute("data-ward-id") as string;
        const newRoomButton = document.querySelector(`[data-ward-id='${id}']`) as HTMLButtonElement;
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
            newBedListener2(newRoom, newBedPrototype);
            addRemovalEventListeners2(newRoom);
        });
    });

    wardForm.addEventListener("submit", (event) => {
        event.preventDefault();
        (wardForm.querySelector("#rooms") as HTMLInputElement).value = gatherRoomData2();
        wardForm.submit();
    });
});
