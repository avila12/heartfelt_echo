#!/bin/bash

# Update and install system dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install -y chromium-browser python3 python3-pip python3-venv unclutter xdotool nginx

# Variables
APP_DIR="$HOME/heartfelt_echo"
STATIC_DIR="$APP_DIR/static"
PHOTOS_DIR="$APP_DIR/photos"
SERVICE_FILE="/etc/systemd/system/heartfelt_echo.service"
NGINX_CONF="/etc/nginx/sites-available/heartfelt_echo"

# Clone the project (if not already cloned)
if [ ! -d "$APP_DIR" ]; then
  git clone https://github.com/avila12/heartfelt_echo.git "$APP_DIR"
fi

cd "$APP_DIR" || { echo "Failed to access project directory"; exit 1; }

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
  pip install -r requirements.txt
fi

# Install Gunicorn
pip install gunicorn

# Create a Gunicorn service
sudo bash -c "cat <<EOF > $SERVICE_FILE
[Unit]
Description=Gunicorn instance to serve Heartfelt Echo
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=$APP_DIR
Environment=\"PATH=$APP_DIR/venv/bin\"
ExecStart=$APP_DIR/venv/bin/gunicorn --workers 3 --bind unix:$APP_DIR/heartfelt_echo.sock wsgi:app

[Install]
WantedBy=multi-user.target
EOF"

# Reload systemd and start the service
sudo systemctl daemon-reload
sudo systemctl enable heartfelt_echo
sudo systemctl start heartfelt_echo

# Configure Nginx
sudo bash -c "cat <<EOF > $NGINX_CONF
server {
    listen 80;
    server_name localhost;

    # Handle static files (CSS, JS, images)
    location /static/ {
        alias $STATIC_DIR/;
    }

    location /photos/ {
        alias $PHOTOS_DIR/;
    }

    # Proxy pass for the Flask application
    location / {
        include proxy_params;
        proxy_pass http://unix:$APP_DIR/heartfelt_echo.sock;
    }
}
EOF"

# Enable the Nginx configuration
sudo ln -sf $NGINX_CONF /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Create an autostart entry for kiosk mode
AUTOSTART_DIR="$HOME/.config/autostart"
mkdir -p "$AUTOSTART_DIR"

cat <<EOF > "$AUTOSTART_DIR/heartfelt_echo.desktop"
[Desktop Entry]
Type=Application
Exec=/bin/bash -c 'chromium-browser --kiosk --noerrdialogs --disable-infobars --disable-translate http://localhost'
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Heartfelt Echo Kiosk
EOF

# Add unclutter to hide mouse cursor
echo "@unclutter -idle 0.5" >> "$HOME/.xinitrc"

echo "Installation complete. Reboot your Raspberry Pi to apply the changes."