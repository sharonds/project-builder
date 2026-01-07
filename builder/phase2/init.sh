#!/bin/bash
# Project Builder Phase 2 - Environment Setup Script
# This script sets up the development environment for the Request Processing System

set -e

echo "=== Project Builder Phase 2 Setup ==="
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Error: Python 3.11+ required. Found: $PYTHON_VERSION"
    echo "Please install Python 3.11 or later."
    exit 1
fi

echo "Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To activate the environment:"
echo "  source venv/bin/activate"
echo ""
echo "Available commands:"
echo "  project-builder analyze <path>     - Analyze existing project"
echo "  project-builder request '<desc>'   - Process feature/bug request"
echo "  project-builder create <name>      - Create new project"
echo "  project-builder run               - Run coding agent"
echo "  project-builder status            - Show feature progress"
echo ""
