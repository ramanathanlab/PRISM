#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load version definitions
source versions.env

# Check if venv already exists
if [ -d ".venv-isaacsim" ]; then
    echo "WARNING: .venv-isaacsim already exists"
    read -p "Delete and recreate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf .venv-isaacsim
        echo "Deleted existing environment"
    else
        echo "Aborting setup"
        exit 1
    fi
fi

# Step 1: Create virtual environment
echo "Creating virtual environment (Python 3.11)..."
uv venv .venv-isaacsim -p python@3.11

# Step 2: Compile requirements
echo ""
echo "Compiling dependencies..."
source .venv-isaacsim/bin/activate
uv pip compile requirements-isaacsim.in \
    --extra-index-url https://pypi.nvidia.com \
    -o requirements-isaacsim.txt

# Step 3: Install dependencies
echo ""
echo "Installing dependencies..."
uv pip sync requirements-isaacsim.txt

deactivate

echo "========================================="
echo "Isaac Sim Environment Setup Complete!"
echo "Activate with: source activate-isaacsim.sh"
