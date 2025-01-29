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

# shellcheck shell=bash
# This file contains utility functions which can be used in the tools.
# Do not execute it directly, but include it with `source`.

# shellcheck source=./tools/utils/docker.sh
source "$(dirname "${BASH_SOURCE[0]}")/docker.sh"
# shellcheck source=./tools/utils/logging.sh
source "$(dirname "${BASH_SOURCE[0]}")/logging.sh"
# shellcheck source=./tools/utils/permissions.sh
source "$(dirname "${BASH_SOURCE[0]}")/permissions.sh"

# Do not continue execution if one of the commands fail
set -eo pipefail -o functrace

# Check if the --verbose option is given
if [[ "$*" == *"--verbose"* ]]; then
    # The shell writes a trace for each command to standard error after it expands the command and before it executes it.
    set -vx
fi
# The Port on which the HospiTool development server should be started (do not use 9000 since this is used for webpack)
HOSPITOOL_PORT=8086
# The name of the used database docker container
DOCKER_CONTAINER_NAME="hospitool_django_postgres"
HOSPITOOL="hospitool"

# Change to dev tools directory
cd "$(dirname "${BASH_SOURCE[0]}")"
# The absolute path to the dev tools directory
cd ..
DEV_TOOL_DIR=$(pwd)
# Change to base directory
cd ..
# The absolute path to the base directory of the repository
BASE_DIR=$(pwd)
# The path to the package
PACKAGE_DIR_REL="hospitool"
PACKAGE_DIR="${BASE_DIR}/${PACKAGE_DIR_REL}"
# The filename of the currently running script
SCRIPT_NAME=$(basename "$0")
# The absolute path to the currently running script (required to allow restarting with different permissions
SCRIPT_PATH="${DEV_TOOL_DIR}/${SCRIPT_NAME}"
# The arguments which were passed to the currently running script
SCRIPT_ARGS=("$@")
# The verbosity of the output (can be one of {0,1,2,3})
SCRIPT_VERBOSITY="1"

# This function shows a success message once the HospiTool development server is running
function listen_for_devserver {
    until nc -z localhost "$HOSPITOOL_PORT"; do sleep 0.1; done
    echo "✔ Started HospiTool at http://localhost:${HOSPITOOL_PORT}" | print_success
}

# This function makes sure a database is available
function require_database {
    # Check if local postgres server is running
    if [[ "$(env bash -c "command -v docker")" ]]; then
         echo "✔ Docker detected" | print_success
        # Set docker settings
        export DJANGO_SETTINGS_MODULE="hospitool.core.docker_settings"
        # Make sure a docker container is up and running
        ensure_docker_container_running
    elif nc -z localhost 5432; then
        ensure_not_root
        echo "✔ Running PostgreSQL database detected" | print_success
        # Migrate database
        migrate_database

        # Set default settings for other dev tools, e.g. testing
        export DJANGO_SETTINGS_MODULE="hospitool.core.settings"
    else
        echo -e "Docker or PostgresQL are required for running this project."  | print_error
        exit 1
    fi
}

# This function migrates the database
function migrate_database {
    # Check for the variable DATABASE_MIGRATED to prevent multiple subsequent migration commands
    if [[ -z "$DATABASE_MIGRATED" ]]; then
        echo "Migrating database..." | print_info
        # Make sure the migrations directory exists
        deescalate_privileges mkdir -pv "${PACKAGE_DIR}/cms/migrations"
        deescalate_privileges touch "${PACKAGE_DIR}/cms/migrations/__init__.py"
        # Generate migration files
        deescalate_privileges hospitool-cli makemigrations --verbosity "${SCRIPT_VERBOSITY}"
        # Execute migrations
        deescalate_privileges hospitool-cli migrate --verbosity "${SCRIPT_VERBOSITY}"
        echo "✔ Finished database migrations" | print_success
        DATABASE_MIGRATED=1
    fi

    # Load permissions fixture
    deescalate_privileges hospitool-cli loaddata permissions
}


# This function checks if the HospiTool is installed
function require_installed {
    if [[ -z "$HOSPITOOL_INSTALLED" ]]; then
        echo "Checking if HospiTool is installed..." | print_info
        # Check if script was invoked with sudo
        if [[ $(id -u) == 0 ]] && [[ -n "$SUDO_USER" ]]; then
            # overwrite $HOME directory in case script was called with sudo but without the -E flag
            HOME="$(bash -c "cd ~${SUDO_USER} && pwd")"
        fi
        # Check if virtual environment exists
        if [[ -f ".venv/bin/activate" ]]; then
            # Activate virtual environment
            # shellcheck disable=SC1091
            source .venv/bin/activate
        else
            echo -e "The virtual environment for this project is missing. Please install it with:\n"  | print_error
            echo -e "\t$(dirname "${BASH_SOURCE[0]}")/install.sh\n" | print_bold
            exit 1
        fi
        # Check if hospitool-cli is available in virtual environment
        if [[ ! -x "$(env bash -c "command -v hospitool-cli")" ]]; then
            echo -e "The HospiTool is not installed. Please install it with:\n"  | print_error
            echo -e "\t$(dirname "${BASH_SOURCE[0]}")/install.sh\n" | print_bold
            exit 1
        fi
        echo "✔ HospiTool is installed" | print_success
        HOSPITOOL_INSTALLED=1
        export HOSPITOOL_INSTALLED
        # Check if script is running in CircleCI context and set DEBUG=True if not
        if [[ -z "$CIRCLECI" ]]; then
            # Set debug mode for
            HOSPITOOL_DEBUG=1
            export HOSPITOOL_DEBUG
        fi
    fi
}

# This function applies different sed replacements to make sure the matched lines from grep are aligned and colored
function format_grep_output {
    while read -r line; do
        echo "$line" | sed --regexp-extended \
            -e "s/^([0-9])([:-])(.*)/\1\2      \3/"         `# Pad line numbers with 1 digit` \
            -e "s/^([0-9]{2})([:-])(.*)/\1\2     \3/"       `# Pad line numbers with 2 digits` \
            -e "s/^([0-9]{3})([:-])(.*)/\1\2    \3/"        `# Pad line numbers with 3 digits` \
            -e "s/^([0-9]{4})([:-])(.*)/\1\2   \3/"         `# Pad line numbers with 4 digits` \
            -e "s/^([0-9]{5})([:-])(.*)/\1\2  \3/"          `# Pad line numbers with 5 digits` \
            -e "s/^([0-9]+):(.*)/\x1b[1;31m\1\2\x1b[0;39m/" `# Make matched line red` \
            -e "s/^([0-9]+)-(.*)/\1\2/"                     `# Remove dash of unmatched line`
    done
}
