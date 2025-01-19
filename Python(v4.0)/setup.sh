#!/bin/bash
set -e

# Install Poetry if you haven't already
if ! command -v poetry &> /dev/null; then
    echo "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
fi

# Create a new project if not in one
if [ ! -f "pyproject.toml" ]; then
    echo "Creating new Poetry project..."
    poetry new document-intelligence-samples
    cd document-intelligence-samples
fi

# Install dependencies
echo "Installing dependencies..."
poetry install

# Create .env from template if it doesn't exist
if [ ! -f ".env" ] && [ -f ".env.template" ]; then
    echo "Creating .env file from template..."
    cp .env.template .env
    echo "Please update .env with your credentials"
fi

echo "Setup complete! Don't forget to:"
echo "1. Update .env with your Azure credentials"
echo "2. Run 'poetry shell' to activate the virtual environment" 