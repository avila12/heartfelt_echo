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
