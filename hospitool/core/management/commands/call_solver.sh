#!/bin/bash

cd "$1" || exit 1
source .venv/bin/activate
python call_from_django.py "$2" "$3"
