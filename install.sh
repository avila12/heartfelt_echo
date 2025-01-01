#!/bin/bash

# Update and install system dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install -y chromium-browser python3 python3-pip python3-venv nginx

# Variables
APP_DIR="$HOME/heartfelt_echo"
STATIC_DIR="/heartfelt_echo/static"
PHOTOS_DIR="/heartfelt_echo/photos"
SERVICE_FILE="/etc/systemd/system/heartfelt_echo.service"
NGINX_CONF="/etc/nginx/sites-available/heartfelt_echo"

cd "$APP_DIR" || { echo "Failed to access project directory"; exit 1; }

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
  pip install -r requirements.txt
fi

sudo chmod 755 .env
sudo chown -R pi:www-data .env


sudo chmod -R 755 /home/pi/heartfelt_echo/static
sudo chown -R pi:www-data /home/pi/heartfelt_echo/static

sudo chmod -R 755 /home/pi/heartfelt_echo/photos
sudo chown -R pi:www-data /home/pi/heartfelt_echo/photos

sudo chown -R pi:www-data /home/pi/heartfelt_echo

sudo chmod 755 /home/pi
sudo chmod 755 /home/pi/heartfelt_echo



#sudo nano /etc/nginx/sites-enabled/flask_app
#curl -I http://192.168.10.128/static/css/app.css

# Install Gunicorn
pip install gunicorn

#sudo nano /etc/systemd/system/gunicorn.service

# Create a Gunicorn service
sudo bash -c "cat <<EOF > $SERVICE_FILE
[Unit]
Description=Gunicorn instance to serve Flask app
After=network.target

[Service]
User=pi
Group=www-data
WorkingDirectory=/home/pi/heartfelt_echo
ExecStart=/home/pi/heartfelt_echo/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app

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
    server_name 10.0.0.161;

    # Handle static files
    location /static/ {
        alias /home/pi/heartfelt_echo/static/;
        autoindex on;  # Optional for debugging, can be removed in production
    }

    # Handle photo files
    location /photos/ {
        alias /home/pi/heartfelt_echo/photos/;  # Use alias for consistency
        autoindex on;  # Optional for debugging, can be removed in production
    }

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    error_page 404 /404.html;
    location = /404.html {
        root /usr/share/nginx/html;
    }
}
EOF"

/home/alexvila/heartfelt_echo/venv/bin/gunicorn --workers 3 --bind unix:/home/alexvila/heartfelt_echo/heartfelt_echo.sock wsgi:app

sudo chown www-data:www-data /home/alexvila/heartfelt_echo/heartfelt_echo.sock
sudo chmod 664 /home/alexvila/heartfelt_echo/heartfelt_echo.sock

# Enable the Nginx configuration
sudo ln -sf $NGINX_CONF /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

echo "Installation complete. The kiosk mode has been removed. You can manually open Chromium and navigate to http://localhost if desired."
