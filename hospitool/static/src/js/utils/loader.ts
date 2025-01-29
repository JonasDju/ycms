const showLoader = () => {
    const loader = document.getElementById("loader-container");
    if (loader) {
        loader.classList.remove("hidden");
    }
};

window.addEventListener("beforeunload", () => {
    const TIMEOUT = 200;
    setTimeout(showLoader, TIMEOUT);
});

window.addEventListener("unload", () => {
    const loader = document.getElementById("loader-container");
    if (loader) {
        loader.classList.add("hidden");
    }
});
