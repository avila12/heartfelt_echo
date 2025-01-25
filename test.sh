#!/bin/bash

# Function to handle errors
handle_error() {
  echo "Error: $1"
  exit 1
}

# Check if the user is root
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root. Please use sudo."
    exit 1
fi

# Variables
HOSTNAME=$(hostname) # Get the Raspberry Pi's hostname
USER_HOME=$(getent passwd pi | cut -d: -f6)
APP_DIR="$USER_HOME/heartfelt_echo"
STATIC_DIR="$APP_DIR/static"
PHOTOS_DIR="$APP_DIR/photos"
SERVICE_FILE="/etc/systemd/system/heartfelt_echo.service"
NGINX_CONF="/etc/nginx/sites-available/heartfelt_echo"

# Ensure the application directory exists
echo "Checking application directory..."
if [ ! -d "$APP_DIR" ]; then
  echo "Directory $APP_DIR does not exist. Please ensure it is created."
  exit 1
fi

cd "$APP_DIR" || handle_error "Failed to access project directory: $APP_DIR"