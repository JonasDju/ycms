#!/bin/bash

# Function to compute SHA256 hash of a file
compute_hash() {
    sha256sum "$1" | awk '{ print $1 }'
}

# Change directory to make sure to ignore files in the venv
cd ycms || exit 1

# Execute the makemessages command update the .po files
echo "Scanning Python and HTML source code and extracting translatable strings from it..."
ycms-cli makemessages -l de --add-location file --verbosity 1

# Compute the SHA256 hash of the file
FILE_PATH="locale/de/LC_MESSAGES/django.po"
CURRENT_HASH=$(compute_hash "$FILE_PATH")

# Define the path for the hash file
HASH_FILE="../.dockercache/locale/de/LC_MESSAGES/django.po.sha256"

# Check if the hash file exists
if [ -f "$HASH_FILE" ]; then
    # Read the stored hash from the file
    STORED_HASH=$(cat "$HASH_FILE")

    # Compare the computed hash with the stored hash
    if [ "$CURRENT_HASH" == "$STORED_HASH" ]; then
        echo "No updated translations found."
    else
        echo "Translation file has been modified. Recompiling..."
        ycms-cli compilemessages --verbosity 1
        echo "$CURRENT_HASH" > "$HASH_FILE"
    fi
else
    # If the hash file does not exist, create it and compile messages
    echo "Compiling translations..."
    ycms-cli compilemessages --verbosity 1
    mkdir -p "$(dirname "$HASH_FILE")"
    echo "$CURRENT_HASH" > "$HASH_FILE"
fi
