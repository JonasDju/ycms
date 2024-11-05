#!/bin/bash

# Function to compute SHA256 hash of a file
compute_hash() {
    sha256sum "$1" | awk '{ print $1 }'
}

# Function to check and install Python dependencies
check_python_deps() {
    local file="pyproject.toml"
    local hash_file=".packagestate/${file}.sha256"
    local current_hash=$(compute_hash "$file")

    if [ ! -f "$hash_file" ]; then
        echo "Installing Python dependencies..."
        pip install -e .[dev-pinned,pinned]
        echo "$current_hash" > "$hash_file"
    else
        local stored_hash=$(cat "$hash_file")
        if [ "$current_hash" != "$stored_hash" ]; then
            echo "Hash mismatch for $file. Installing Python dependencies..."
            pip install -e .[dev-pinned,pinned]
            echo "$current_hash" > "$hash_file"
        else
            echo "No updated Python requirements found."
        fi
    fi
}

# Function to check and install Node.js dependencies
check_node_deps() {
    local file="package.json"
    local lock_file="package-lock.json"
    local hash_file=".packagestate/${file}.sha256"
    local lock_hash_file=".packagestate/${lock_file}.sha256"
    local current_hash=$(compute_hash "$file")
    local current_lock_hash=$(compute_hash "$lock_file")

    if [ ! -f "$hash_file" ] || [ ! -f "$lock_hash_file" ]; then
        echo "Installing JavaScript dependencies..."
        npm install --no-fund
        echo "$current_hash" > "$hash_file"
        echo "$current_lock_hash" > "$lock_hash_file"
    else
        local stored_hash=$(cat "$hash_file")
        local stored_lock_hash=$(cat "$lock_hash_file")
        if [ "$current_hash" != "$stored_hash" ] || [ "$current_lock_hash" != "$stored_lock_hash" ]; then
            echo "Hash mismatch for JavaScript dependencies. Installing JavaScript dependencies..."
            npm install --no-fund
            echo "$current_hash" > "$hash_file"
            echo "$current_lock_hash" > "$lock_hash_file"
        else
            echo "No updated JavaScript requirements found."
        fi
    fi
}

# Ensure the .packagestate directory exists
mkdir -p .packagestate

# Check and install Python dependencies
check_python_deps

# Check and install Node.js dependencies
check_node_deps
