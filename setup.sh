#!/bin/bash

# InfoFlow MCP Server Setup Script
# This script automates the installation and setup process

set -e

echo "╔════════════════════════════════════════════════════╗"
echo "║        InfoFlow MCP Server Setup                   ║"
echo "║    Combat Information Overload & Decision Fatigue  ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}Error: Python 3.11 or higher is required. Found: $PYTHON_VERSION${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists. Skipping...${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Create config file if it doesn't exist
echo ""
if [ ! -f "config.json" ]; then
    echo "Creating configuration file..."
    cp config.example.json config.json
    echo -e "${GREEN}✓ Configuration file created${NC}"
else
    echo -e "${YELLOW}Configuration file already exists. Skipping...${NC}"
fi

# Initialize database
echo ""
echo "Initializing database..."
python3 << EOF
from server import DatabaseManager
db = DatabaseManager()
print("Database initialized successfully!")
EOF
echo -e "${GREEN}✓ Database initialized${NC}"

# Test the server
echo ""
echo "Testing server startup..."
timeout 2s python server.py || true
echo -e "${GREEN}✓ Server test completed${NC}"

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║              Setup Complete! 🎉                    ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
echo "Next Steps:"
echo "1. Run the server: python server.py"
echo "2. Configure ChatGPT Custom GPT using custom_gpt_instructions.md"
echo "3. Test the integration"
echo ""
echo "For detailed instructions, see README.md"
echo ""
echo "To start the server now, run:"
echo -e "${GREEN}  source venv/bin/activate${NC}"
echo -e "${GREEN}  python server.py${NC}"
echo ""