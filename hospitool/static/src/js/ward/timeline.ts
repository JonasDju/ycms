import { Timeline, TimelineOptions } from "vis-timeline";
import { DataSet } from "vis-data";

type Id = number | string;

type TimelineItem = {
    id: number;
    content: string;
    start: string;
    end: string;
    requiredBeds: number;
    group: Id;
    className: string;
};

type GroupItem = {
    id: Id;
    content: string;
    beds: number;
};

type Change = {
    assignmentId: number;
    roomId: number;
};

const maxConcurrentBeds = (unsortedObjects: TimelineItem[]) => {
    const objects = unsortedObjects.sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime());
    let maxConcurrentBeds = 0;
    for (let i = 0; i < objects.length; i++) {
        let concurrentBeds: number = objects[i].requiredBeds;
        for (let j = i + 1; i < objects.length; j++) {
            if (j >= objects.length || objects[i].end < objects[j].start) {
                break;
            }
            concurrentBeds += objects[j].requiredBeds;
        }
        maxConcurrentBeds = Math.max(maxConcurrentBeds, concurrentBeds);
    }
    return maxConcurrentBeds;
};

const showUnsaved = (totalChanges: number) => {
    const changeCounterContainer = document.querySelector("#change-counter") as HTMLElement;
    const changeCounter = document.querySelector("#change-counter span") as HTMLElement;
    const autosuggest = document.querySelector("#autosuggest") as HTMLElement;
    if (!changeCounterContainer || !changeCounter || !autosuggest) {
        return;
    }

    changeCounter.innerHTML = String(totalChanges);
    if (totalChanges > 0) {
        changeCounterContainer.classList.remove("hidden");
        autosuggest.classList.add("hidden");
    } else {
        changeCounterContainer.classList.add("hidden");
        autosuggest.classList.remove("hidden");
    }
};

class ChangeTracker {
    changeList: Change[] = [];
    constructor(items: DataSet<TimelineItem>, initialChanges: Change[]) {
        this.changeList = initialChanges;
        showUnsaved(this.changeList.length);

        items.forEach((item) => {
            if (this.changeList.some((change) => change.assignmentId === item.id)) {
                // eslint-disable-next-line no-param-reassign
                item.className += " changed";
            }
        });
    }
    trackChange = (assignmentId: number, roomId: number) => {
        const existingAssignment = this.changeList.find((a) => a.assignmentId === assignmentId);
        if (existingAssignment) {
            existingAssignment.roomId = roomId;
        } else {
            this.changeList.push({ assignmentId, roomId });
        }
        return this.changeList.length;
    };
    serialize = () => JSON.stringify(this.changeList);
}

window.addEventListener("load", () => {
    const timelineContainer = document.querySelector("#timeline-container") as HTMLElement;
    const changesForm = document.querySelector("#timeline-changes-form") as HTMLFormElement;
    const changesInput = document.querySelector("#timeline-changes") as HTMLInputElement;
    const changesButton = document.querySelector("#timeline-changes-form button") as HTMLButtonElement;
    if (!timelineContainer || !changesForm || !changesInput || !changesButton) {
        return;
    }

    /* eslint-disable-next-line @typescript-eslint/no-explicit-any */
    const items = new DataSet<TimelineItem>(JSON.parse((globalThis as any).timeline_items as string));
    /* eslint-disable-next-line @typescript-eslint/no-explicit-any */
    const groups = new DataSet<GroupItem>(JSON.parse((globalThis as any).timeline_groups as string));
    /* eslint-disable-next-line @typescript-eslint/no-explicit-any */
    const suggestions = JSON.parse((globalThis as any).timeline_suggestions as string) as Change[];

    const changeTracker = new ChangeTracker(items, Object.keys(suggestions).length ? suggestions : []);

    changesButton.addEventListener("click", (event) => {
        event.preventDefault();
        changesInput.value = changeTracker.serialize();
        changesForm.submit();
    });

    const options: TimelineOptions = {
        groupHeightMode: "auto",
        autoResize: false,
        editable: { updateGroup: true, overrideItems: true },
        margin: { axis: 5, item: { horizontal: 0 } },
        rollingMode: { follow: true, offset: 0.1 },
        orientation: { axis: "top", item: "top" },
        // Called every time we move an item, regardless of if we drop it into a group
        onMoving: (item, callback) => {
            // Always allow unassigning
            if ((item.group as string) === "unassigned") {
                return callback(item);
            }

            // This produces an array containing all bed assignments which overlap with the item we are moving
            const concurrentStays = items.get({
                filter: (testItem) => {
                    if (testItem.id === item.id || testItem.group !== item.group) {
                        return false;
                    }
                    return !((item.end as Date) < new Date(testItem.start) || item.start > new Date(testItem.end));
                },
            });

            const maxOccupants = groups.get(item.group as Id)?.beds || Infinity;
            const requiredBeds = (item as TimelineItem).requiredBeds;
            if (maxConcurrentBeds(concurrentStays) + requiredBeds <= maxOccupants) {
                callback(item);
            }

            // This is just vis-timelines way of not executing the move
            return callback(null);
        },
        // Only called once we drop the item into a group
        onMove: (item, callback) => {
            const totalChanges = changeTracker.trackChange(item.id as number, item.group as number);
            showUnsaved(totalChanges);
            // eslint-disable-next-line no-param-reassign
            item.className += " changed";
            callback(item);
        },
    };

    const timeline = new Timeline(timelineContainer, items, groups, options);

    // If we are timetravelling, center the timeline on the travelled-to time
    const urlParams = new URLSearchParams(window.location.search);
    const timeParameter = urlParams.get("time");
    if (!timeParameter) {
        return;
    }
    const dateTime = new Date(timeParameter.replace("Z", "+01:00"));
    timeline.toggleRollingMode();
    timeline.addCustomTime(dateTime);
    timeline.setCurrentTime(dateTime);
    timeline.moveTo(dateTime, { animation: false });
});
