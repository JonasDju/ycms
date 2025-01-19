#!/bin/bash

# Check if the folder ../patient-to-room_assignment exists
if [ ! -d "../patient-to-room_assignment" ]; then
    exit 1
fi

# Activate the virtual environment
source ../patient-to-room_assignment/.venv/bin/activate

# Check if the gurobi license file exists
if [ ! -f "gurobi/gurobi.lic" ]; then
    exit 2
fi

# Execute the check_license.py script
python tools/check_gurobi_license.py
SCRIPT_EXIT_CODE=$?

# Handle the exit code of the Python script
if [ $SCRIPT_EXIT_CODE -eq 0 ]; then
    exit 0
elif [ $SCRIPT_EXIT_CODE -eq 1 ]; then
    exit 3
fi