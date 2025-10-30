#!/bin/bash
# Key Lab Setup

cd "$(dirname "$0")"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade packages
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup complete! Run ./run.sh to start the application."
