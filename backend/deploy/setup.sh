#!/bin/bash

# Deployment Setup Script for EmergentIntelliTest
# This script sets up the production environment

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting EmergentIntelliTest Deployment Setup${NC}"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}❌ Python 3 is required but not installed. Please install Python 3.8 or higher.${NC}"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))' | cut -d. -f1-2)
if [[ "$PYTHON_VERSION" < "3.8" ]]; then
    echo -e "${YELLOW}❌ Python 3.8 or higher is required. Found Python $PYTHON_VERSION${NC}"
    exit 1
fi

# Create virtual environment
echo -e "\n${GREEN}🔧 Setting up Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate  # On Windows, use: .\venv\Scripts\activate

# Install dependencies
echo -e "\n${GREEN}📦 Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Set up environment variables
echo -e "\n${GREEN}⚙️  Setting up environment variables...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}ℹ️  Please update the .env file with your configuration.${NC}"
else
    echo -e "${GREEN}✅ .env file already exists.${NC}"
fi

# Set up database
echo -e "\n${GREEN}💾 Setting up database...${NC}"
python -c "from app.db.init_db import init; init()"

# Run migrations (if using Alembic)
if [ -f "alembic.ini" ]; then
    echo -e "\n${GREEN}🔄 Running database migrations...${NC}"
    alembic upgrade head
fi

# Create necessary directories
echo -e "\n${GREEN}📁 Creating necessary directories...${NC}"
mkdir -p logs
mkdir -p uploads

# Set permissions
echo -e "\n${GREEN}🔒 Setting file permissions...${NC}"
chmod -R 755 .
chmod +x scripts/*.sh

# Install system dependencies (if needed)
if [ "$EUID" -eq 0 ]; then
    echo -e "\n${GREEN}🛠️  Installing system dependencies...${NC}"
    # Add any system dependencies here
    # Example: apt-get update && apt-get install -y python3-dev python3-venv
fi

echo -e "\n${GREEN}✨ Setup completed successfully!${NC}"
echo -e "\nTo start the application in development mode, run: ${YELLOW}uvicorn app.main:app --reload${NC}"
echo -e "For production, use a production server like Gunicorn with Uvicorn workers."

exit 0
