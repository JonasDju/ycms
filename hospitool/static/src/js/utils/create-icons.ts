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
import { icons } from "lucide";
import replaceElement from "lucide/dist/esm/replaceElement";

// This function renders all <i icon-name="..."> children of `root`
export const createIconsAt = (root: HTMLElement) => {
    const elementsToReplace = root.querySelectorAll("[icon-name]");
    Array.from(elementsToReplace).forEach((element) =>
        replaceElement(element as HTMLElement, {
            nameAttr: "icon-name",
            icons,
            attrs: { class: "inline-block" },
        }),
    );
};
