#!/bin/bash

# Production Deployment Script for EmergentIntelliTest
# This script deploys the application in a production environment

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="emergent-intellitest"
APP_USER="intellitest"
APP_GROUP="www-data"
APP_DIR="/opt/$APP_NAME"
VENV_DIR="$APP_DIR/venv"
LOG_DIR="/var/log/$APP_NAME"
CONFIG_DIR="/etc/$APP_NAME"
SERVICE_NAME="$APP_NAME.service"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Please run as root${NC}"
    exit 1
fi

echo -e "${GREEN}🚀 Starting $APP_NAME Deployment${NC}"

# Create application directory
echo -e "\n${GREEN}📁 Creating application directories...${NC}"
mkdir -p $APP_DIR
mkdir -p $LOG_DIR
mkdir -p $CONFIG_DIR

# Copy application files
echo -e "\n${GREEN}📦 Copying application files...${NC}"
cp -r . $APP_DIR/
chown -R $APP_USER:$APP_GROUP $APP_DIR
chmod -R 750 $APP_DIR

# Set up Python virtual environment
echo -e "\n${GREEN}🐍 Setting up Python virtual environment...${NC}"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv $VENV_DIR
fi

# Activate virtual environment and install dependencies
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install -r $APP_DIR/requirements.txt

# Set up environment variables
echo -e "\n${GREEN}⚙️  Setting up environment variables...${NC}"
if [ ! -f "$CONFIG_DIR/.env" ]; then
    cp $APP_DIR/.env.example $CONFIG_DIR/.env
    echo -e "${YELLOW}ℹ️  Please update the configuration in $CONFIG_DIR/.env${NC}"
    ln -sf $CONFIG_DIR/.env $APP_DIR/.env
else
    ln -sf $CONFIG_DIR/.env $APP_DIR/.env
    echo -e "${GREEN}✅ Using existing configuration from $CONFIG_DIR/.env${NC}"
fi

# Set up database
echo -e "\n${GREEN}💾 Setting up database...${NC}" 
sudo -u $APP_USER bash -c "cd $APP_DIR && source $VENV_DIR/bin/activate && python -c 'from app.db.init_db import init; init()'"

# Run migrations (if using Alembic)
if [ -f "$APP_DIR/alembic.ini" ]; then
    echo -e "\n${GREEN}🔄 Running database migrations...${NC}"
    cd $APP_DIR
    alembic upgrade head
fi

# Set up systemd service
echo -e "\n${GREEN}🔧 Setting up systemd service...${NC}"
cat > /etc/systemd/system/$SERVICE_NAME <<EOL
[Unit]
Description=EmergentIntelliTest API Service
After=network.target

[Service]
User=$APP_USER
Group=$APP_GROUP
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001 --workers 4
Restart=always
RestartSec=5

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=full
ProtectHome=true
ReadWritePaths=$LOG_DIR

# Logging
StandardOutput=append:$LOG_DIR/app.log
StandardError=append:$LOG_DIR/error.log

[Install]
WantedBy=multi-user.target
EOL

# Set permissions
echo -e "\n${GREEN}🔒 Setting file permissions...${NC}"
chown -R $APP_USER:$APP_GROUP $LOG_DIR
chmod -R 750 $LOG_DIR
chmod 640 $CONFIG_DIR/.env

# Enable and start service
echo -e "\n${GREEN}🚀 Starting $APP_NAME service...${NC}"
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl restart $SERVICE_NAME

# Check service status
SERVICE_STATUS=$(systemctl is-active $SERVICE_NAME)
if [ "$SERVICE_STATUS" = "active" ]; then
    echo -e "${GREEN}✅ $APP_NAME is now running!${NC}"
    echo -e "\n${GREEN}✨ Deployment completed successfully!${NC}"
    echo -e "\nApplication URL: http://your-server-ip:8001"
    echo -e "API Documentation: http://your-server-ip:8001/docs"
    echo -e "\nView logs with: ${YELLOW}journalctl -u $SERVICE_NAME -f${NC}"
else
    echo -e "${RED}❌ Failed to start $APP_NAME service${NC}"
    echo -e "Check logs with: ${YELLOW}journalctl -u $SERVICE_NAME -n 50 --no-pager${NC}"
    exit 1
fi

exit 0
