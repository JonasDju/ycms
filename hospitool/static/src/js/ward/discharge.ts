import { Modal, ModalOptions } from "flowbite";

let selectedBedAssignmentId: string | null = "";

const handleModalClose = (): void => {
    document.getElementById("cancelDischargeButton")?.addEventListener("click", () => {
        const modal = FlowbiteInstances.getInstance("Modal", "modalEl");
        modal.hide();
    });
    document.getElementById("closeModalButton")?.addEventListener("click", () => {
        const modal = FlowbiteInstances.getInstance("Modal", "modalEl");
        modal.hide();
    });
};

const handleConfirmDischarge = (): void => {
    document.getElementById("confirmDischargeButton")?.addEventListener("click", () => {
        const form = document.querySelector(`#discharge-${selectedBedAssignmentId}`) as HTMLFormElement;
        form?.submit();
    });
};

const handleDischarge = (button: HTMLElement): void => {
    selectedBedAssignmentId = button.getAttribute("data-bedassignment-id");

    const targetEl = document.getElementById("modalEl");

    const options: ModalOptions = {
        placement: "center-center" as ModalOptions["placement"],
        backdrop: "dynamic",
        backdropClasses: "bg-gray-900 bg-opacity-50 dark:bg-opacity-80 fixed inset-0 z-[40]",
        closable: true,
    };
    const modal = new Modal(targetEl, options);
    modal.show();
};

const handleButtonDischarge = (): void => {
    const buttons = document.querySelectorAll<HTMLElement>(".discharge-button");

    buttons.forEach((element) => {
        element.addEventListener("click", () => {
            handleDischarge(element);
        });
    });
};

window.addEventListener("load", () => {
    handleButtonDischarge();
    handleConfirmDischarge();
    handleModalClose();
});
