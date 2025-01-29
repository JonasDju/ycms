const SIDEBAR_THRESHOLD_WIDTH = 1024;

window.addEventListener("load", () => {
    const sidebarOpen = document.getElementById("sidebarOpen");
    const sidebarClose = document.getElementById("sidebarClose");
    const sidebar = document.getElementById("sidebar");
    const leftToggle = document.getElementById("leftToggle");
    const mainContent = document.getElementById("mainContent");
    const sidebarBackdrop = document.getElementById("sidebarBackdrop");

    // if  localStorage isSidebarOpen not set, set it to true
    if (localStorage.getItem("isSidebarOpen") === null) {
        localStorage.setItem("isSidebarOpen", "true");
    }

    const isSidebarOpen = localStorage.getItem("isSidebarOpen") === "true";

    if (!isSidebarOpen && sidebar) {
        sidebar?.classList.toggle("lg:translate-x-0");
        mainContent?.classList.toggle("lg:ml-64");
    }

    if (sidebarOpen && sidebar) {
        sidebarOpen.addEventListener("click", () => {
            sidebar.classList.remove("-translate-x-full");
            sidebar.classList.add("lg:translate-x-0");
            sidebarClose?.classList.remove("hidden");
            sidebarBackdrop?.classList.remove("hidden");

            localStorage.setItem("isSidebarOpen", "true");
        });
    }

    const closeSidebar = () => {
        if (sidebar && sidebarClose && sidebarBackdrop) {
            sidebar.classList.add("-translate-x-full");
            sidebar.classList.remove("lg:translate-x-0");
            sidebarClose.classList.add("hidden");
            sidebarBackdrop.classList.add("hidden");
            localStorage.setItem("isSidebarOpen", "false");
        }
    };

    if (sidebarClose) {
        sidebarClose.addEventListener("click", closeSidebar);
    }

    if (sidebarBackdrop) {
        sidebarBackdrop.addEventListener("click", closeSidebar);
    }

    leftToggle?.addEventListener("click", () => {
        const isLocalStorageSidebarOpen = localStorage.getItem("isSidebarOpen") === "true";
        const isCurrentOpen = sidebar?.classList.contains("lg:translate-x-0");
        const isXFull = sidebar?.classList.contains("-translate-x-full");

        if (isCurrentOpen) {
            sidebar?.classList.remove("lg:translate-x-0");
            mainContent?.classList.remove("lg:ml-64");
        } else {
            sidebar?.classList.add("lg:translate-x-0");
            mainContent?.classList.add("lg:ml-64");
        }

        if (isLocalStorageSidebarOpen && !isXFull) {
            sidebar?.classList.add("-translate-x-full");
        }

        // Update localStorage with the current state
        const isOpen = sidebar?.classList.contains("lg:translate-x-0");
        localStorage.setItem("isSidebarOpen", String(isOpen));
    });
});

window.addEventListener("resize", () => {
    const isSidebarOpen = localStorage.getItem("isSidebarOpen") === "true";
    const windowWidth = window.innerWidth;
    const mainContent = document.getElementById("mainContent");

    if (windowWidth >= SIDEBAR_THRESHOLD_WIDTH) {
        mainContent?.classList.toggle("lg:ml-64", isSidebarOpen);
    }
});
