window.addEventListener("load", () => {
    const progressBarElements = document.querySelectorAll(".progress-bar");
    progressBarElements.forEach((progressBar) => {
        const dataProgress = progressBar.getAttribute("data-progress");
        const progressPercentage: number = dataProgress ? parseInt(dataProgress, 10) : 0;
        progressBar.setAttribute("style", `--progress-width: ${progressPercentage}%`);
    });
});
