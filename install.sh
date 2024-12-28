#!/bin/bash

# Update and install system dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install -y chromium-browser python3 python3-pip unclutter xdotool

# Install Gunicorn for running the Flask app
pip3 install gunicorn

# Clone or pull the latest version of the repository
APP_DIR="$HOME/heartfelt_echo"
if [ ! -d "$APP_DIR" ]; then
  git clone https://github.com/avila12/heartfelt_echo.git "$APP_DIR"
else
  cd "$APP_DIR" && git pull
fi

# Navigate to the app directory
cd "$APP_DIR"

# Install Python dependencies
if [ -f "requirements.txt" ]; then
  pip3 install -r requirements.txt
fi

# Create a Gunicorn service
SERVICE_FILE="/etc/systemd/system/heartfelt_echo.service"
sudo bash -c "cat <<EOF > $SERVICE_FILE
[Unit]
Description=Gunicorn instance to serve Heartfelt Echo
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=$APP_DIR
Environment=\"PATH=$APP_DIR/venv/bin\"
ExecStart=/usr/local/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 wsgi:app

[Install]
WantedBy=multi-user.target
EOF"

# Reload systemd and start the service
sudo systemctl daemon-reload
sudo systemctl enable heartfelt_echo
sudo systemctl start heartfelt_echo

# Create an autostart entry for kiosk mode
AUTOSTART_DIR="$HOME/.config/autostart"
mkdir -p "$AUTOSTART_DIR"

cat <<EOF > "$AUTOSTART_DIR/heartfelt_echo.desktop"
[Desktop Entry]
Type=Application
Exec=/bin/bash -c 'chromium-browser --kiosk --noerrdialogs --disable-infobars --disable-translate --app=http://localhost:8000'
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Heartfelt Echo Kiosk
EOF

# Add unclutter to hide mouse cursor
echo "@unclutter -idle 0.5" >> "$HOME/.xinitrc"

echo "Installation complete. Reboot your Raspberry Pi to see the app in kiosk mode."