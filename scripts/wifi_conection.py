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
        # Update wpa_supplicant.conf
        with open(WPA_SUPPLICANT_CONF, "w") as file:
            file.write(
                f"""
            ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
            update_config=1
            country=US

            network={{
                ssid="{ssid}"
                psk="{password}"
            }}
            """
            )

        # Schedule a system reboot
        subprocess.run(["sudo", "reboot"])

        return True
    except Exception as e:
        return False