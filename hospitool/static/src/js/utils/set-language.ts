const getUserBrowserLanguage = (): string => {
    const userLanguage = navigator.language.split("-")[0];
    return ["de", "en"].includes(userLanguage) ? userLanguage : "en";
};

const checkLanguageCookie = (): boolean =>
    !!document.cookie.split("; ").find((cookie) => cookie.startsWith("django_language="));

const setLanguageCookie = (language: string): void => {
    document.cookie = `django_language=${language}; path=/;`;
};

const addClassesToElement = (elementId: string, classes: string): void => {
    if (!elementId.length) {
        return;
    }
    const element = document.getElementById(elementId);
    if (element) {
        element.classList.add(...classes.split(" "));
    }
};

const handleLanguageSwitch = (): void => {
    if (!checkLanguageCookie()) {
        const userLanguage = getUserBrowserLanguage();
        setLanguageCookie(userLanguage);

        const elementId = `lang-switch-${userLanguage}`;
        const classesToAdd = "underline pointer-events-none text-gray-300 dark:text-gray-500";

        addClassesToElement(elementId, classesToAdd);
    }
};

window.addEventListener("load", () => {
    handleLanguageSwitch();
});
