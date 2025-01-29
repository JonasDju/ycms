#!/bin/bash

# Switch into the hospitool base dir and activate python environment
cd hospitool
. .venv/bin/activate

# Specify DJANGO_SETTINGS_MODULE for pytest to work with
export DJANGO_SETTINGS_MODULE="hospitool.core.settings"

# Delete outdated code coverage report
CODE_COVERAGE_DIR="htmlcov"
rm -rf "${CODE_COVERAGE_DIR}"

# Parse given command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        # If only tests affected by recent changed should be run, --changed can be passed as a flag
        --changed) CHANGED=1;shift;;
        # Verbosity for pytest
        -v|-vv|-vvv|-vvvv) VERBOSITY="$1";shift;;
        # If only particular tests should be run, test path can be passed as CLI argument
        *) TEST_PATH=$1;shift;;
    esac
done

# The default pytests args we use
PYTEST_ARGS=("--disable-warnings" "--color=yes")

if [[ -n "${VERBOSITY}" ]]; then
    PYTEST_ARGS+=("$VERBOSITY")
else
    PYTEST_ARGS+=("--quiet" "--numprocesses=auto")
fi

# Check if --changed flag was passed
if [[ -n "${CHANGED}" ]]; then
    # Check if .testmondata file exists
    if [[ -f ".testmondata" ]]; then
        # Only run changed tests and don't update dependency database
        PYTEST_ARGS+=("--testmon-nocollect")
        CHANGED_MESSAGE=" affected by recent changes"
    else
        # Inform that all tests will be run
        echo -e "\nIt looks like you have not run pytest without the \"--changed\" flag before."
        echo -e "Pytest has to build a dependency database by running all tests without the flag once.\n"
        # Override test path argument
        unset TEST_PATH
        # Tell testmon to run all tests and collect data
        PYTEST_ARGS+=("--testmon-noselect")
    fi
else
    # Run all tests, but update list of tests
    PYTEST_ARGS+=("--testmon-noselect")
fi

# Determine whether coverage data should be collected
if [[ -z "${CHANGED}" && -z "${TEST_PATH}" ]]; then
    PYTEST_ARGS+=("--cov=hospitool" "--cov-report=html")
fi

# Check whether test path exists
if [[ -e "${TEST_PATH}" ]]; then
    # Adapt message and append to pytest arguments
    TEST_MESSAGE=" in ${TEST_PATH}"
    PYTEST_ARGS+=("${TEST_PATH}")
elif [[ -n "${TEST_PATH}" ]]; then
    # If the test path does not exist but was non-zero, show an error
    echo -e "${TEST_PATH}: No such file or directory"
    exit 1
fi

echo -e "Running all tests${TEST_MESSAGE}${CHANGED_MESSAGE}..."
pytest "${PYTEST_ARGS[@]}"
echo "✔ Tests successfully completed"

if [[ -d "${CODE_COVERAGE_DIR}" ]]; then
    echo -e "Open the following file in your browser to view the test coverage:\n"
    echo -e "\t${CODE_COVERAGE_DIR}/index.html\n"
fi
