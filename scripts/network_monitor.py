import os
import time
import netifaces
import subprocess


NGINX_CONFIG = "/etc/nginx/sites-available/heartfelt_echo"


def is_wifi_connected(interface="wlan0"):
    """Check if the given interface is connected to a network."""
    try:
        addrs = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addrs:
            ip_info = addrs[netifaces.AF_INET][0]
            return ip_info.get("addr")
    except ValueError:
        pass
    return None


def update_nginx_config(wifi_ip):
    """Update Nginx configuration with the current Wi-Fi IP."""
    with open(NGINX_CONFIG, "r") as file:
        config = file.read()

    # Replace the placeholder with the Wi-Fi IP
    updated_config = config.replace("__WI-FI_IP__", wifi_ip)

    with open(NGINX_CONFIG, "w") as file:
        file.write(updated_config)

    # Reload Nginx to apply changes
    subprocess.run(["sudo", "nginx", "-t"])
    subprocess.run(["sudo", "systemctl", "reload", "nginx"])


def monitor_network():
    """Monitor network status and switch between modes."""
    last_wifi_ip = None
    while True:
        wifi_ip = is_wifi_connected()
        if wifi_ip and wifi_ip != last_wifi_ip:
            print(f"Wi-Fi connected: {wifi_ip}")
            update_nginx_config(wifi_ip)
            last_wifi_ip = wifi_ip
        elif not wifi_ip and last_wifi_ip:
            print("Wi-Fi disconnected. Switching to AP mode.")
            # Optionally start AP services here
            last_wifi_ip = None

        time.sleep(5)


if __name__ == "__main__":
    monitor_network()
