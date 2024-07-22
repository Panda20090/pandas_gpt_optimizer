#!/bin/bash

# Ensure the project root directory is set
if [ -z "$PROJECT_ROOT" ]; then
  echo "PROJECT_ROOT environment variable is not set."
  exit 1
fi

# Navigate to the GPT directory
cd "$PROJECT_ROOT/GPT" || exit

# Check if the virtual environment exists
if [ ! -d "setup/venv" ]; then
  # Create a new virtual environment if it does not exist
  python -m venv setup/venv
fi

# Activate the virtual environment
if [ -f "setup/venv/bin/activate" ]; then
  source "setup/venv/bin/activate"
else
  echo "Could not find the virtual environment activation script."
  exit 1
fi

# Install necessary dependencies
pip install -r requirements.txt
pip install openai flask

# Append to the project's requirements.txt
cat requirements.txt >> "$PROJECT_ROOT/requirements.txt"

echo "Environment setup complete."
