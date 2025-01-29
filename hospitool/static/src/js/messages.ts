// Copyright [2019] [Integreat Project]
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
const minDisplayTime = 4000;
const fadeOutOffset = 700;

const fadeMessages = (
    messages: NodeListOf<HTMLDivElement> | HTMLDivElement[],
    index: number,
    offsetOverwrite?: number,
) => {
    if (index >= messages.length) {
        return;
    }

    setTimeout(() => {
        /* eslint-disable-next-line no-param-reassign */
        messages[messages.length - 1 - index].style.opacity = "0";
        fadeMessages(messages, index + 1);
        setTimeout(() => {
            messages[messages.length - 1 - index].remove();
        }, fadeOutOffset);
    }, offsetOverwrite ?? fadeOutOffset);
};

window.addEventListener("load", () => {
    const messagesContainer = document.getElementById("messages");
    if (!messagesContainer) {
        return;
    }
    const messages = messagesContainer.querySelectorAll("div");

    messages.forEach((message) => {
        message.querySelector(".message-close")?.addEventListener("click", () => {
            fadeMessages([message], 0, 0);
        });
    });

    setTimeout(() => {
        fadeMessages(messages, 0);
    }, minDisplayTime);
});
