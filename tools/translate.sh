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

# This script can be used to re-generate the translation file and compile it. It is also executed in run.sh

# Import utility functions
# shellcheck source=./tools/utils/_functions.sh
source "$(dirname "${BASH_SOURCE[0]}")/utils/_functions.sh"

require_installed
ensure_not_root

# Change directory to make sure to ignore files in the venv
cd "${PACKAGE_DIR}" || exit 1

# Relative path from package directory
TRANSLATION_FILE="locale/de/LC_MESSAGES/django.po"

# Re-generating translation file
echo "Scanning Python and HTML source code and extracting translatable strings from it..." | print_info
ycms-cli makemessages -l de --add-location file --verbosity "${SCRIPT_VERBOSITY}"

# Reset POT-Creation-Date to avoid git conflicts
sed --in-place --regexp-extended 's/^"POT-Creation-Date: [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}\+[0-9]{4}\\n"$/"POT-Creation-Date: YEAR-MO-DA HO:MI+ZONE\\n"/' "${TRANSLATION_FILE}"

# Skip compilation if --skip-compile option is given
if [[ "$*" != *"--skip-compile"* ]]; then
    # Compile translation file
    echo "Compiling translation file..." | print_info
    ycms-cli compilemessages --verbosity "${SCRIPT_VERBOSITY}"
fi

echo "✔ Translation process finished" | print_success
