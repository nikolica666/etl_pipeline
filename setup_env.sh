#!/bin/bash
# =========================================
# Setup script for ETL project
# =========================================

# Exit on error
set -e

echo "=== Creating virtual environment ==="
python -m venv venv

echo "=== Activating virtual environment ==="
# Linux/macOS
source venv/bin/activate
# Windows (PowerShell)
# venv\Scripts\Activate.ps1

echo "=== Upgrading pip ==="
pip install --upgrade pip

echo "=== Installing project in editable mode ==="
pip install -e .

# Optional: install dev dependencies if requirements-dev.txt exists
if [ -f requirements-dev.txt ]; then
    echo "=== Installing development dependencies ==="
    pip install -r requirements-dev.txt
fi

echo "=== Setup complete ==="
echo "Activate the environment with: source venv/bin/activate"