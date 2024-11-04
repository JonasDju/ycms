#!/bin/bash

cd ycms

# This function shows a success message once the YCMS development server is running
function listen_for_devserver {
    until nc -z localhost "$YCMS_PORT"; do sleep 0.1; done
    echo "✔ Started YCMS at http://localhost:${YCMS_PORT}"
}

# Install JavaScript dependencies
echo "Installing JavaScript dependencies..."
npm install --no-fund
echo "✔ Installed JavaScript dependencies"

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

# Install pip dependencies
echo "Installing Python dependencies..."
pip install -e .[dev-pinned,pinned]
echo "✔ Installed Python dependencies"

# Perform migration (if required)
echo "Performing migrations if required..."
ycms-cli makemigrations
ycms-cli migrate
echo "✔ Finished database migrations"

# Loading test data
echo "Loading test data..."
ycms-cli loaddata "ycms/cms/fixtures/permissions.json"
ycms-cli loaddata "ycms/cms/fixtures/hospital_data.json"
ycms-cli loaddata "ycms/cms/fixtures/test_data_icd10.json"
ycms-cli loaddata "ycms/cms/fixtures/test_data.json"
ycms-cli loaddata "ycms/cms/fixtures/final_test_data_icd10.json"
ycms-cli loaddata "ycms/cms/fixtures/final_test_data.json"
echo "✔ Loaded test data"

# Check if compiled webpack output exists
if [[ -z $(compgen -G "ycms/static/dist/main.*.js") ]]; then
    echo -e "The compiled static files do not exist yet, therefore the start of the Django dev server will be delayed until the initial WebPack build is completed."
fi

echo "Starting WebPack dev server in background..."
npm run dev 2>&1 &

# Waiting for initial WebPack dev build
while [[ -z $(compgen -G "ycms/static/dist/main.*.js") ]]; do
    sleep 1
done

# Show success message once dev server is up
listen_for_devserver &
ycms-cli runserver "0.0.0.0:${YCMS_PORT}"
