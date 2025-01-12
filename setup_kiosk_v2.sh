#!/bin/bash

# Function to handle errors
handle_error() {
  echo "Error: $1"
  exit 1
}

# 0. Get the Raspberry Pi's hostname
HOSTNAME=$(hostname)

###################################
# 1. Update & install dependencies
###################################
echo "Updating and upgrading the system..."
sudo apt update && sudo apt upgrade -y || handle_error "Failed to update and upgrade packages"

echo "Installing system dependencies..."
sudo apt install -y \
  chromium-browser \
  python3 python3-pip python3-venv \
  nginx avahi-daemon \
  python3-rpi.gpio \
  hostapd dnsmasq git php-fpm php-cli php-common php-curl php-json \
  || handle_error "Failed to install required packages"

# Remove any existing lighttpd if you prefer not to keep it
sudo apt remove --purge -y lighttpd || echo "lighttpd not installed, continuing..."

# Optional cleanup
sudo apt autoremove -y

###################################
# 2. Set up your Flask application
###################################
APP_DIR="$HOME/heartfelt_echo"
STATIC_DIR="$APP_DIR/static"
PHOTOS_DIR="$APP_DIR/photos"
SERVICE_FILE="/etc/systemd/system/heartfelt_echo.service"
NGINX_CONF="/etc/nginx/sites-available/heartfelt_echo"

# Ensure the application directory exists
cd "$APP_DIR" || handle_error "Failed to access project directory: $APP_DIR"

# Set up Python virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv || handle_error "Failed to create virtual environment"
source venv/bin/activate || handle_error "Failed to activate virtual environment"

echo "Installing Python dependencies..."
pip install --upgrade pip || handle_error "Failed to upgrade pip"
if [ -f "$APP_DIR/requirements.txt" ]; then
  pip install -r "$APP_DIR/requirements.txt" || handle_error "Failed to install dependencies from requirements.txt"
else
  echo "No requirements.txt found, skipping installation of Python dependencies."
fi

# Set permissions
echo "Configuring permissions for Flask app..."
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
Environment=\"FLASK_ENV=production\"
ExecStart=$APP_DIR/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
EOF"

echo "Enabling and starting the Gunicorn service..."
sudo systemctl daemon-reload || handle_error "Failed to reload systemd"
sudo systemctl enable heartfelt_echo || handle_error "Failed to enable Gunicorn service"
sudo systemctl start heartfelt_echo || handle_error "Failed to start Gunicorn service"

###################################
# 3. Install RaspAP (Manual / Nginx)
###################################
echo "Installing RaspAP core files (without lighttpd)..."

# Clone RaspAP webgui into /var/www/html/raspap (or wherever you like):
sudo mkdir -p /var/www/html
sudo git clone https://github.com/RaspAP/raspap-webgui.git /var/www/html/raspap || handle_error "Failed to clone RaspAP"

# Set ownership/permissions
sudo chown -R www-data:www-data /var/www/html/raspap
sudo find /var/www/html/raspap -type f -exec chmod 644 {} \;
sudo find /var/www/html/raspap -type d -exec chmod 755 {} \;

# RaspAP needs hostapd + dnsmasq config:
#   - The official installer writes /etc/dhcpcd.conf, /etc/hostapd/hostapd.conf, /etc/dnsmasq.conf, etc.
#   - For brevity, we’re only demonstrating the web UI approach with Nginx here.
#   - You will need to configure hostapd + dnsmasq manually for your AP.

###################################
# 4. Configure Nginx for RaspAP
###################################
# We will serve RaspAP from /raspap/ and your Flask app from the root or another location
echo "Configuring Nginx with reverse proxy for RaspAP..."

sudo bash -c "cat <<EOF > $NGINX_CONF
server {
    listen 80;
    server_name $HOSTNAME.local;

    client_max_body_size 16M;

    # Serve the RaspAP admin interface at /raspap/
    location /raspap/ {
        alias /var/www/html/raspap/;
        index index.php;
        try_files \$uri \$uri/ /index.php?\$args;
    }

    # PHP-FPM handling for RaspAP .php files
    location ~ \.php\$ {
        # Adjust PHP-FPM version if necessary
        fastcgi_pass unix:/run/php/php-fpm.sock;
        fastcgi_index index.php;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME \$request_filename;
    }

    # Your Flask app at the root /
    location /static/ {
        alias $STATIC_DIR/;
        autoindex off;
    }

    location /photos/ {
        alias $PHOTOS_DIR/;
        autoindex off;
    }

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }

    # Security headers
    add_header X-Frame-Options "DENY";
    add_header X-Content-Type-Options "nosniff";
    add_header X-XSS-Protection "1; mode=block";
}
EOF"

# Enable the site and reload Nginx
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/
sudo nginx -t || handle_error "Nginx configuration test failed"
sudo systemctl restart nginx || handle_error "Failed to restart Nginx"

###################################
# 5. Kiosk Mode Setup (Chromium)
###################################
echo "Configuring Chromium in kiosk mode..."

# Enable autologin for the 'pi' user
echo "Enabling autologin for user 'pi'..."
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
{
  echo "[Service]"
  echo "ExecStart="
  echo "ExecStart=-/sbin/agetty --noclear --autologin pi %I \$TERM"
} | sudo tee /etc/systemd/system/getty@tty1.service.d/override.conf

# Create .xinitrc to launch Chromium
echo "Creating /home/pi/.xinitrc to start Chromium in kiosk mode..."
cat << 'EOF' > /home/pi/.xinitrc
#!/bin/bash
xset s off
xset -dpms
xset s noblank
xrandr --output HDMI-1 --rotate left  # For portrait mode, adjust as needed
chromium-browser --noerrdialogs --kiosk http://localhost --incognito --disable-translate --start-fullscreen
EOF
chmod +x /home/pi/.xinitrc

# Auto-start X on login
echo "Configuring system to start X automatically on login..."
if ! grep -q "startx" /home/pi/.bash_profile; then
  echo "if [ -z \"\$DISPLAY\" ] && [ \$(tty) = /dev/tty1 ]; then" >> /home/pi/.bash_profile
  echo "  startx" >> /home/pi/.bash_profile
  echo "fi" >> /home/pi/.bash_profile
fi

# Optionally disable LightDM if installed
# sudo systemctl disable lightdm

# Disable screen blanking in Openbox
echo "Disabling screen blanking and power management in Openbox..."
sudo mkdir -p /etc/xdg/openbox
{
  echo "xset s off"
  echo "xset -dpms"
  echo "xset s noblank"
} | sudo tee -a /etc/xdg/openbox/autostart

# Hide the mouse cursor after a short idle
echo "Hiding the mouse cursor with unclutter..."
echo "unclutter -idle 0.1 -root &" >> /home/pi/.xinitrc

###################################
# 6. Final Reboot
###################################
echo "Setup complete! Rebooting the Raspberry Pi..."
sudo reboot
