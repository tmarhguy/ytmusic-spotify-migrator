#!/bin/bash
# Export requirements for different environments

echo "Exporting requirements..."

# Main requirements
pip freeze > requirements.txt

# Development requirements
echo "# Development requirements" > requirements-dev.txt
echo "# Generated from pyproject.toml[project.optional-dependencies.dev]" >> requirements-dev.txt
pip list --format=freeze | grep -E "(pytest|mypy|ruff|black|pre-commit|responses|freezegun)" >> requirements-dev.txt

echo "Requirements exported to:"
echo "  - requirements.txt (main dependencies)"
echo "  - requirements-dev.txt (dev dependencies)"
