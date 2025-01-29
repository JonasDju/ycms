import { initFlowbite } from "flowbite";

window.addEventListener("load", () => {
    // ensure flowbite is initialized before we try anything
    initFlowbite();
    const openers = document.querySelectorAll<HTMLElement>("[data-drawer-show]");
    const closers = document.querySelectorAll<HTMLElement>("[data-drawer-hide]");

    openers.forEach((opener) => {
        opener.addEventListener("click", () => {
            localStorage.setItem("openDrawer", opener.dataset.drawerTarget as string);
            const backdrop = document.querySelector("[drawer-backdrop]") as HTMLElement;
            backdrop.addEventListener("click", () => {
                localStorage.removeItem("openDrawer");
            });
        });
    });

    closers.forEach((closer) => {
        closer.addEventListener("click", () => {
            localStorage.removeItem("openDrawer");
        });
    });

    const urlParams = new URLSearchParams(window.location.search);
    const passedDrawer = urlParams.get("drawer");
    const toOpen = passedDrawer || localStorage.getItem("openDrawer");
    if (!toOpen) {
        return;
    }

    const drawer = document.querySelector(`[data-drawer-show="${toOpen}"]`) as HTMLElement;
    if (!drawer) {
        return;
    }
    drawer.dispatchEvent(new Event("click"));
});
