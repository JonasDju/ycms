#!/bin/bash
# Copyright [2019] [Integreat Project]
# Copyright [2023] [YCMS]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This script can be used to resolve git merge/rebase conflicts of the translation file

# Import utility functions
# shellcheck source=./tools/utils/_functions.sh
source "$(dirname "${BASH_SOURCE[0]}")/utils/_functions.sh"

require_installed
ensure_not_root

# Relative path to translation file from the base directory
TRANSLATION_FILE="hospitool/locale/de/LC_MESSAGES/django.po"

echo "Resolving translation conflicts..." | print_info

# Remove git conflict markers
sed --in-place --regexp-extended -e '/^<<<<<<< .+$/d' -e '/^=======$/d' -e '/^>>>>>>> .+$/d' "$TRANSLATION_FILE"

# Remove duplicated translations and show error if this is not possible
if ! msguniq --output-file "$TRANSLATION_FILE" "$TRANSLATION_FILE" 2>&1 \
  | sed --regexp-extended -e "s|^(${TRANSLATION_FILE}):([0-9]+):[0-9]+?:? (.+)$|\1 \x1b[1m(line \2) \x1b[1;31m\3\x1b[0;39m|g" -e "$ d"; then
    echo -e "\n❌ Not all conflicts could be solved automatically" | print_error
    echo "Please fix the mentioned problem(s) manually and run this script again." | print_bold
    exit 1
fi

# Check if conflicts remain
if grep --quiet "#-#-#-#-#" "$TRANSLATION_FILE"; then
    echo -e "\n$TRANSLATION_FILE"
    grep --before-context=2 --after-context=1 --line-number "#-#-#-#-#" "$TRANSLATION_FILE" | format_grep_output | print_with_borders
    echo -e "❌ Not all conflicts could be solved automatically" | print_error
    echo "Please resolve remaining conflicts (marked with \"#-#-#-#-#\") manually and run this script again." | print_bold
    exit 1
fi

echo "✔ All conflicts were successfully resolved" | print_success

# Check if status is "unmerged"
if git status --short "$TRANSLATION_FILE" | grep --quiet "UU ${TRANSLATION_FILE}"; then
    # Mark conflict as resolved by adding to the staging area
    git add "$TRANSLATION_FILE"
    GIT_ADD_TO_STAGING_AREA=1
fi

# Fix line numbers and empty lines
bash "${DEV_TOOL_DIR}/translate.sh"

if [[ -n "$GIT_ADD_TO_STAGING_AREA" ]]; then
    # If conflict was marked as resolved before, also stage the changed line numbers and removed newlines etc...
    git add "$TRANSLATION_FILE"
fi
