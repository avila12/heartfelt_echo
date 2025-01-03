#!/bin/bash

# Function to handle errors
handle_error() {
  echo "Error: $1"
  exit 1
}

# Get the Raspberry Pi's hostname
HOSTNAME=$(hostname)

# Update and install system dependencies
echo "Updating system and installing dependencies..."
sudo apt update && sudo apt upgrade -y || handle_error "Failed to update and upgrade packages"
sudo apt install -y chromium-browser python3 python3-pip python3-venv nginx avahi-daemon || handle_error "Failed to install required packages"
sudo apt autoremove

# Variables
APP_DIR="$HOME/heartfelt_echo"
STATIC_DIR="$APP_DIR/static"
PHOTOS_DIR="$APP_DIR/photos"
SERVICE_FILE="/etc/systemd/system/heartfelt_echo.service"
NGINX_CONF="/etc/nginx/sites-available/heartfelt_echo"
KIOSK_DESKTOP="$HOME/.config/autostart/heartfelt_echo_kiosk.desktop"

# Ensure the application directory exists
cd "$APP_DIR" || handle_error "Failed to access project directory: $APP_DIR"

# Set up Python virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv || handle_error "Failed to create virtual environment"
source venv/bin/activate || handle_error "Failed to activate virtual environment"

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip || handle_error "Failed to upgrade pip"
if [ -f "requirements.txt" ]; then
  pip install -r requirements.txt || handle_error "Failed to install dependencies from requirements.txt"
fi

# Set permissions
echo "Configuring permissions..."
sudo chmod 755 .env
sudo chown -R pi:www-data .env

for dir in "$STATIC_DIR" "$PHOTOS_DIR"; do
  sudo chmod -R 755 "$dir"
  sudo chown -R pi:www-data "$dir"
done

sudo chown -R pi:www-data "$APP_DIR"
sudo chmod 755 "$HOME"
sudo chmod 755 "$APP_DIR"

# Install Gunicorn
echo "Installing Gunicorn..."
pip install gunicorn || handle_error "Failed to install Gunicorn"

# Create a Gunicorn service
echo "Creating Gunicorn service..."
sudo bash -c "cat <<EOF > $SERVICE_FILE
[Unit]
Description=Gunicorn instance to serve Flask app
After=network.target

[Service]
User=pi
Group=www-data
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
EOF"

# Reload systemd and start the service
echo "Reloading systemd and starting Gunicorn service..."
sudo systemctl daemon-reload || handle_error "Failed to reload systemd"
sudo systemctl enable heartfelt_echo || handle_error "Failed to enable Gunicorn service"
sudo systemctl start heartfelt_echo || handle_error "Failed to start Gunicorn service"

# Configure Nginx with dynamic hostname
echo "Configuring Nginx..."
sudo bash -c 'cat <<EOF > '"$NGINX_CONF"'
server {
    listen 80;
    server_name '"$HOSTNAME"'.local;

    # Handle static files
    location /static/ {
        alias '"$STATIC_DIR"'/;
        autoindex on; # Optional for debugging, can be removed in production
    }

    # Handle photo files
    location /photos/ {
        alias '"$PHOTOS_DIR"'/; # Use alias for consistency
        autoindex on; # Optional for debugging, can be removed in production
    }

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    error_page 404 /404.html;
    location = /404.html {
        root /usr/share/nginx/html;
    }
}
EOF'

# Remove default Nginx configuration and enable new configuration
sudo rm /etc/nginx/sites-enabled/default
sudo ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/
sudo nginx -t || handle_error "Nginx configuration test failed"
sudo systemctl restart nginx || handle_error "Failed to restart Nginx"

# Configure kiosk mode for Chromium with dynamic hostname
echo "Configuring Chromium in kiosk mode..."
mkdir -p ~/.config/autostart
cat <<EOF > "$KIOSK_DESKTOP"
echo "[Desktop Entry]
Type=Application
Name=Heartfelt Echo Kiosk
Exec=chromium-browser --noerrdialogs --kiosk http://$HOSTNAME.local --start-fullscreen
X-GNOME-Autostart-enabled=true" > "$KIOSK_DESKTOP"

# Set the screen orientation to portrait
echo "Setting screen orientation to portrait mode..."
sudo sh -c 'echo "display_lcd_rotate=1" >> /boot/config.txt'

# Final message
echo "Installation complete. Rebooting now..."
sudo reboot
