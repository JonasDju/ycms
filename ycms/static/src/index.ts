import "tom-select/dist/css/tom-select.css";
import "vis-timeline/styles/vis-timeline-graph2d.css";
import "./css/style.scss";
import "./js/messages";
import "./js/patient-select-or-create";
import "./js/utils/autocomplete";
import "./js/utils/persistent-drawers";
import "./js/utils/timetravel";
import "./js/utils/menu";
import "./js/ward/discharge";
import "./js/ward/assign";
import "./js/ward-management";
import "./js/ward/timeline";
import "./js/ward/toggle-edit-mode";
import "./js/ward/progress";
import { createIconsAt } from "./js/utils/create-icons";
import "./js/patients-list";
import "./js/utils/loader";
import "./js/utils/set-language";
import "./js/patient-intake";

window.addEventListener("DOMContentLoaded", () => {
    createIconsAt(document.documentElement);
    const event = new Event("icon-load");
    window.dispatchEvent(event);
});
