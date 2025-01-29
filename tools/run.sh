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

# This script can be used to start the HospiTool together with a postgres database docker container.
# It also includes generating translation files and applying migrations after the docker container is started for the first time.

# Make sure Webpack background process is terminated when script ends
trap "exit" INT TERM ERR
trap "kill 0" EXIT
KILL_TRAP=1

# Import utility functions
# shellcheck source=./tools/utils/_functions.sh
source "$(dirname "${BASH_SOURCE[0]}")/utils/_functions.sh"

# Require that hospitool is installed
require_installed

# Require that a database server is up and running. Place this command at the beginning because it might require the restart of the script with higher privileges.
require_database

# Skip migrations and translations if --fast option is given
if [[ "$*" != *"--fast"* ]]; then
    # Migrate database
    migrate_database
fi

# Check if compiled webpack output exists
if [[ -z $(compgen -G "${PACKAGE_DIR}/static/dist/main.*.js") ]]; then
    echo -e "The compiled static files do not exist yet, therefore the start of the Django dev server will be delayed until the initial WebPack build is completed." | print_warning
fi

# Starting WebPack dev server in background
echo -e "Starting WebPack dev server in background..." | print_info | print_prefix "webpack" 36
deescalate_privileges npm run dev 2>&1 | print_prefix "webpack" 36 &

# Waiting for initial WebPack dev build
while [[ -z $(compgen -G "${PACKAGE_DIR}/static/dist/main.*.js") ]]; do
    sleep 1
done

# Show success message once dev server is up
listen_for_devserver &

# Start HospiTool development webserver
deescalate_privileges hospitool-cli runserver "localhost:${HOSPITOOL_PORT}"
