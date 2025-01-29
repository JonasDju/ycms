import { Modal, ModalOptions } from "flowbite";

let selectedRoomId: string | null;

const handleAssignModalClose = (): void => {
    document.getElementById("cancelAssignButton")?.addEventListener("click", () => {
        const modal = FlowbiteInstances.getInstance("Modal", "assign-modal");
        modal.hide();
    });
    document.getElementById("closeAssignButton")?.addEventListener("click", () => {
        const modal = FlowbiteInstances.getInstance("Modal", "assign-modal");
        modal.hide();
    });
};

const handleAssignModalConfirm = (): void => {
    document.getElementById("confirmAssignButton")?.addEventListener("click", () => {
        const form = document.querySelector(`#assign-room-${selectedRoomId}`) as HTMLFormElement;
        form?.submit();
    });
};

const handleAssign = (card: HTMLFormElement): void => {
    selectedRoomId = card.getAttribute("data-room-id");
    const roomNumber = card.getAttribute("data-room-number");
    const genderWarning = card.getAttribute("data-room-gender-warning");
    const ageWarning = card.getAttribute("data-room-age-warning");
    const insuranceWarning = card.getAttribute("data-room-insurance-warning");
    const assignModalTextAttr = card.getAttribute("assign-modal-text");
    const warningModalTextAttr = card.getAttribute("warning-modal-text");

    const assignModalText = `
        <h3 class="mb-5 text-lg font-normal text-gray-500 dark:text-gray-400">${assignModalTextAttr}</h3>
    `.replace("{}", roomNumber?.toString() || "");

    let warningList = "";

    if (genderWarning) {
        warningList += `<li>${genderWarning}</li>`;
    }
    if (ageWarning) {
        warningList += `<li>${ageWarning}</li>`;
    }
    if (insuranceWarning) {
        warningList += `<li>${insuranceWarning}</li>`;
    }

    const targetEl = document.getElementById("assign-modal");
    const assignContent = document.getElementById("assign-modal-content");

    const options: ModalOptions = {
        placement: "center-center" as ModalOptions["placement"],
        backdrop: "dynamic",
        backdropClasses: "bg-gray-900 bg-opacity-10 dark:bg-gray-800 dark:bg-opacity-10 fixed inset-0 z-[40]",
        closable: true,
    };

    if (!targetEl) {
        return;
    }
    if (!assignContent) {
        return;
    }
    if (!genderWarning && !ageWarning && !insuranceWarning) {
        assignContent.innerHTML = assignModalText;
    } else {
        assignContent.innerHTML = `
    <div
    class="mb-5 bg-yellow-50 text-yellow-800 p-4 rounded-lg shadow dark:bg-gray-800 dark:text-yellow-300 flex flex-col justify-between h-full">
    <h2 class="text-xl font-semibold text-gray-900 dark:text-white">${warningModalTextAttr}</h2>
    <ul class="max-w-md space-y-2 mt-2 list-disc list-inside dark:text-gray-400">
    ${warningList}
    </ul>
</div>

    ${assignModalText}
        `.replace("{}", roomNumber?.toString() || "");
    }

    const modal = new Modal(targetEl, options);
    modal.show();
};

const handleRoomCardAssign = (): void => {
    const cards = document.querySelectorAll<HTMLFormElement>('div[id*="assignRoomCard"]');

    cards.forEach((element) => {
        element.addEventListener("click", () => {
            handleAssign(element);
        });
    });
};

const handleWardTransfer = () => {
    const wardSelect = document.querySelector("#new_ward_select") as HTMLInputElement;
    if (!wardSelect) {
        return;
    }

    wardSelect.addEventListener("change", () => {
        wardSelect.form?.submit();
    });
};

window.addEventListener("load", () => {
    handleRoomCardAssign();
    handleAssignModalClose();
    handleAssignModalConfirm();
    handleWardTransfer();
});
