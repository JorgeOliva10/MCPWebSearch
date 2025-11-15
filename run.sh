#!/bin/bash

# Startup script for MCP Search Server

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== MCP Search Server ===${NC}"
echo -e "${YELLOW}Privacy-focused web and social media search${NC}"

# Check Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 not found${NC}"
    exit 1
fi

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv .venv
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error creating virtual environment${NC}"
        exit 1
    fi
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Checking dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${RED}Error installing dependencies${NC}"
    exit 1
fi

echo -e "${GREEN}Search server started!${NC}"
echo -e "${YELLOW}Supported engines: DuckDuckGo, Qwant, Brave, Ecosia, Startpage${NC}"
echo -e "${YELLOW}Social platforms: Twitter, Reddit, YouTube, GitHub, StackOverflow, Medium, Pinterest, TikTok, Instagram, Facebook, LinkedIn${NC}"
echo ""

# Start the server
python3 main.py "$@"