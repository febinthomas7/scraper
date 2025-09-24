#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Update the package list and install Chromium and its dependencies
echo "Installing Chromium browser..."
apt-get update -y
apt-get install -y chromium-browser

# Install Python dependencies from requirements.txt
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Build complete!"