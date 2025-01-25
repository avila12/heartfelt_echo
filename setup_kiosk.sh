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


# Update and upgrade the system
echo "Updating and upgrading the system..."
sudo apt update
sudo apt upgrade -y || handle_error "Failed to update and upgrade packages"

sudo apt install -y \
  chromium-browser \
  python3 \
  python3-pip \
  python3-venv \
  nginx \
  avahi-daemon \
  python3-rpi.gpio \
  xserver-xorg \
  xinit \
  openbox \
  unclutter \
  hostapd \
  dnsmasq \
  || handle_error "Failed to install required packages"

sudo apt autoremove -y

# Ensure the application directory exists
cd "$APP_DIR" || handle_error "Failed to access project directory: $APP_DIR"

# Set up Python virtual environment
echo "Setting up Python virtual environment..."
python3 -m venv venv || handle_error "Failed to create virtual environment"
source venv/bin/activate || handle_error "Failed to activate virtual environment"

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip || handle_error "Failed to upgrade pip"
if [ -f "$APP_DIR/requirements.txt" ]; then
  pip install -r "$APP_DIR/requirements.txt" || handle_error "Failed to install dependencies from requirements.txt"
else
  echo "No requirements.txt found, skipping installation of Python dependencies."
fi

git config core.fileMode false

# Set permissions (consider more restrictive permissions for .env if it holds sensitive data)
echo "Configuring permissions..."
sudo chmod 640 .env
sudo chown pi:www-data .env

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

    client_max_body_size 16M;

    location /static/ {
        alias '"$STATIC_DIR"'/;
        autoindex off;
    }

    location /photos/ {
        alias '"$PHOTOS_DIR"'/;
        autoindex off;
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

    add_header X-Frame-Options "DENY";
    add_header X-Content-Type-Options "nosniff";
    add_header X-XSS-Protection "1; mode=block";
}
EOF'

# Remove default Nginx configuration and enable new configuration
sudo rm /etc/nginx/sites-enabled/default
sudo ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/
sudo nginx -t || handle_error "Nginx configuration test failed"
sudo systemctl restart nginx || handle_error "Failed to restart Nginx"
sudo systemctl status nginx || handle_error "Nginx service failed to start"

# new code
echo "Setting up permissions for nmcli..."

# Get the username of the user running the script
read -p "Enter the username to grant nmcli permissions [default: pi]: " USERNAME
USERNAME=${USERNAME:-pi}  # Default to 'pi' if no input is provided

if id "$USERNAME" &>/dev/null; then
    echo "Granting $USERNAME permission to use nmcli without sudo..."
else
    echo "Error: User $USERNAME does not exist."
    exit 1
fi

echo "pi ALL=(ALL) NOPASSWD: /usr/bin/nmcli" | sudo tee -a /etc/sudoers


# Validate the username
if id "$USERNAME" &>/dev/null; then
    echo "Granting $USERNAME permission to use nmcli without sudo..."
else
    echo "Error: User $USERNAME does not exist."
    exit 1
fi

# Add nmcli to sudoers for the specified user
SUDOERS_LINE="$USERNAME ALL=(ALL) NOPASSWD: /usr/bin/nmcli"
if ! grep -Fxq "$SUDOERS_LINE" /etc/sudoers; then
    echo "$SUDOERS_LINE" >> /etc/sudoers
    echo "Added nmcli permissions to sudoers for $USERNAME."
else
    echo "User $USERNAME already has permissions for nmcli."
fi

# Enable Wi-Fi if disabled
echo "Enabling Wi-Fi..."
nmcli radio wifi on

# Check and start NetworkManager if not running
if ! systemctl is-active --quiet NetworkManager; then
    echo "Starting NetworkManager..."
    systemctl start NetworkManager
    systemctl enable NetworkManager
    echo "NetworkManager started and enabled to run at boot."
else
    echo "NetworkManager is already running."
fi

echo "Setup complete. You can now run the Flask app!"


# end new code




echo "Configuring Chromium in kiosk mode..."

# Enable autologin for the 'pi' user
echo "Enabling autologin for user 'pi'..."
sudo mkdir -p /etc/systemd/system/getty@tty1.service.d
{
  echo "[Service]"
  echo "ExecStart="
  echo "ExecStart=-/sbin/agetty --noclear --autologin pi %I \$TERM"
} | sudo tee /etc/systemd/system/getty@tty1.service.d/override.conf

# Configure the X server to start Chromium in kiosk mode
echo "Creating .xinitrc file to start Chromium in kiosk mode..."
cat <<EOF > /home/pi/.xinitrc
#!/bin/bash
xset s off
xset -dpms
xset s noblank
xrandr --output HDMI-1 --rotate left
chromium-browser --noerrdialogs --kiosk http://$HOSTNAME.local --incognito --disable-translate --start-fullscreen
EOF

chmod +x /home/pi/.xinitrc

# Configure the system to start X automatically on login
echo "Configuring system to start X automatically on login..."
{
  echo "if [ -z \"\$DISPLAY\" ] && [ \$(tty) = /dev/tty1 ]; then"
  echo "  startx"
  echo "fi"
} >> /home/pi/.bash_profile

# Disable desktop GUI (LightDM) if desired
echo "Disabling LightDM (GUI) to prevent desktop environment..."
# sudo systemctl disable lightdm

# Disable screen blanking and power management
echo "Disabling screen blanking and power management..."
echo "xset s off" | sudo tee -a /etc/xdg/openbox/autostart
echo "xset -dpms" | sudo tee -a /etc/xdg/openbox/autostart
echo "xset s noblank" | sudo tee -a /etc/xdg/openbox/autostart

# Optional: Hide the mouse cursor
echo "Hiding the mouse cursor after idle..."
echo "unclutter -idle 0.1 -root &" | sudo tee -a /home/pi/.xinitrc

# Reboot the system to apply changes
echo "Setup complete! Rebooting the Raspberry Pi..."
sudo reboot
