#!/bin/bash

#Define cleanup procedure
cleanup() {
    # Execute the makemessages command update the .po files on exit
    cd "hospitool"
    hospitool-cli makemessages -l de --add-location file --verbosity 0
}

#Trap SIGTERM -> execute cleanup procedure
trap 'cleanup' SIGTERM


# Change into the hospitool directory
cd hospitool

# Temporary solution to migrate users from .packagestate to .dockercache
if [ -d ".packagestate" ]; then
    echo "Migrating from .packagestate to .dockercache"
    mv .packagestate .dockercache
    mkdir -p .dockercache/packages

    # Move all files (package hashes) into the newly created packages folder
    mv .dockercache/* .dockercache/packages/ 2>/dev/null
fi


# This function shows a success message once the HospiTool development server is running
function listen_for_devserver {
    until nc -z localhost "$HOSPITOOL_PORT"; do sleep 0.1; done
    echo "✔ Started HospiTool at http://localhost:${HOSPITOOL_PORT}"
}

# Check if python virtual environment exists
if [[ ! -f ".venv/bin/activate" ]]; then
    echo "Creating virtual environment for $(${PYTHON} --version)..."
    # Check whether venv creation succeeded
    if ! ${PYTHON} -m venv .venv; then
        echo "Creation of virtual environment failed..."
        exit 1
    fi
fi

# Activate virtual environment
source .venv/bin/activate

# Install python and js dependencies
../install_dependencies.sh

# Update translation files and compile if required
../translate.sh

# Perform migration (if required)
echo "Performing migrations if required..."
hospitool-cli makemigrations
hospitool-cli migrate
echo "✔ Finished database migrations"

# Loading test data
echo "Loading test data..."
hospitool-cli loaddata "hospitool/cms/fixtures/permissions.json"
hospitool-cli loaddata "hospitool/cms/fixtures/hospital_data.json"
hospitool-cli loaddata "hospitool/cms/fixtures/test_data_icd10.json"
hospitool-cli loaddata "hospitool/cms/fixtures/test_data.json"
hospitool-cli loaddata "hospitool/cms/fixtures/final_test_data_icd10.json"
hospitool-cli loaddata "hospitool/cms/fixtures/final_test_data.json"
hospitool-cli loaddata "hospitool/cms/fixtures/specializations_data.json"
echo "✔ Loaded test data"

# Check if compiled webpack output exists
if [[ -z $(compgen -G "hospitool/static/dist/main.*.js") ]]; then
    echo -e "The compiled static files do not exist yet, therefore the start of the Django dev server will be delayed until the initial WebPack build is completed."
fi

echo "Starting WebPack dev server in background..."
npm run dev 2>&1 &

# Waiting for initial WebPack dev build
while [[ -z $(compgen -G "hospitool/static/dist/main.*.js") ]]; do
    sleep 1
done

# Show success message once dev server is up
listen_for_devserver &
hospitool-cli runserver "0.0.0.0:${HOSPITOOL_PORT}" &

wait $!
