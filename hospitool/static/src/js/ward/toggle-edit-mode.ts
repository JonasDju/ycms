window.addEventListener("load", () => {
    const toggleEditButtons = document.querySelectorAll<HTMLElement>(".toggle-edit-button");
    toggleEditButtons.forEach((button) => {
        button.addEventListener("click", () => {
            const parentCard = button.parentNode?.parentNode?.parentNode as HTMLElement;
            let otherCard = parentCard?.nextElementSibling as HTMLElement;
            if (!otherCard) {
                otherCard = parentCard?.previousElementSibling as HTMLElement;
            }
            if (!parentCard || !otherCard) {
                return;
            }
            parentCard.classList.toggle("hidden");
            otherCard.classList.toggle("hidden");
        });
    });
});
