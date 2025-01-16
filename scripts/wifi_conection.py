import subprocess

import netifaces


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


def get_wifi_status():
    try:
        # Check connected Wi-Fi SSID
        result = subprocess.run(["iwgetid", "-r"], capture_output=True, text=True)
        ssid = result.stdout.strip()

        # Check internet connectivity
        internet_status = subprocess.run(
            ["ping", "-c", "1", "8.8.8.8"], capture_output=True
        )
        connected_to_internet = internet_status.returncode == 0

        return {
            "connected": bool(ssid),
            "ssid": ssid if ssid else None,
            "internet": connected_to_internet,
        }
    except Exception as e:
        return {"connected": False, "error": str(e)}
