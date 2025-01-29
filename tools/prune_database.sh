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

# This script can be used to prune the complete postgres database.
# It stops and removes the docker container and removes all database-related directories.

# Import utility functions
# shellcheck source=./tools/utils/_functions.sh
source "$(dirname "${BASH_SOURCE[0]}")/utils/_functions.sh"

# Check if docker is installed
if command -v docker > /dev/null; then

    # Make sure script has the permission to remove the .postgres directory owned by docker daemon user
    ensure_docker_permission

    # Check if postgres container is running
    if [ "$(docker ps -q -f name="${DOCKER_CONTAINER_NAME}")" ]; then
        # Stop Postgres Docker container
        stop_docker_container
    fi
    # Check if a stopped database container exists
    if [ "$(docker ps -aq -f status=exited -f name="${DOCKER_CONTAINER_NAME}")" ]; then
        # Remove Postgres Docker container
        docker rm "${DOCKER_CONTAINER_NAME}" > /dev/null
        echo "Removed database container" | print_info
    fi

    # Remove database directory
    rm -rfv "${BASE_DIR:?}/.postgres"
    echo "Removed database contents" | print_info

else

    # Check if local postgres server is running
    if nc -w1 localhost 5432; then

        echo "Please delete and re-create your database manually, typically like this:

        user@host$ su postgres
        postgres@host$ psql

        > DROP DATABASE hospitool;
        > CREATE DATABASE hospitool;
    " | print_info
    fi

fi

# Remove media files (because they are no longer usable without the corresponding database entries)
rm -rfv "${PACKAGE_DIR:?}/media"
echo "Removed media files" | print_info
