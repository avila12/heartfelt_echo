import subprocess

import netifaces

WPA_SUPPLICANT_CONF = "/etc/wpa_supplicant/wpa_supplicant.conf"

def is_wifi_connected(interface="wlan0"):
    """Check if the given interface is connected to a network."""
    try:
        addrs = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addrs:
            ip_info = addrs[netifaces.AF_INET][0]
            return "addr" in ip_info and ip_info["addr"] != "127.0.0.1"
    except ValueError:
        pass
    return False


def update_wifi(ssid, password):
    try:
        # Write to the config file with sudo
        config_content = f"""
        ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
        update_config=1
        country=US

        network={{
            ssid="{ssid}"
            psk="{password}"
        }}
        """
        process = subprocess.run(
            ["sudo", "bash", "-c", f"echo '{config_content}' > {WPA_SUPPLICANT_CONF}"],
            check=True
        )

        subprocess.run(["sudo", "systemctl", "stop", "NetworkManager"], check=True)
        subprocess.run(["sudo", "systemctl", "restart", "wpa_supplicant"], check=True)

        # Schedule a system reboot
        subprocess.run(["sudo", "reboot"], check=True)


        return True
    except Exception as e:
        print(e)
        return False