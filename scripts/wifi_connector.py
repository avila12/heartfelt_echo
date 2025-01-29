#!/usr/bin/env python3
import subprocess
import time

def connect_to_wifi(ssid, password):
    try:
        known_networks = subprocess.check_output(
            ['nmcli', '-t', '-f', 'NAME', 'connection', 'show']
        ).decode().splitlines()

        if ssid in known_networks:
            # We already have a connection profile, bring it up
            subprocess.run(
                ['nmcli', 'connection', 'up', ssid],
                check=True,
                capture_output=True,
                text=True
            )
        else:
            # Connect to a new network
            subprocess.run(
                ['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password],
                check=True,
                capture_output=True,
                text=True
            )

        return {"message": f"Successfully connected to '{ssid}'."}

    except subprocess.CalledProcessError as e:
        # e.stderr or e.stdout will contain the nmcli output if we used capture_output=True
        return {"error": f"Failed to connect to '{ssid}'. nmcli output: {e.stderr or e.stdout}"}
    except Exception as ex:
        return {"error": f"An unexpected error occurred: {ex}"}


def get_available_wifi():
    """
    Fetch and display all available Wi-Fi networks using nmcli,
    and return the list of unique SSIDs.
    """
    try:
        # Trigger a Wi-Fi scan
        subprocess.run(['nmcli', 'dev', 'wifi', 'rescan'], check=True)
        time.sleep(2)

        # Get available Wi-Fi networks
        result = subprocess.check_output(['nmcli', '-t', '-f', 'SSID,SIGNAL,BARS,SECURITY', 'dev', 'wifi']).decode()

        # Parse and eliminate duplicate networks
        seen_networks = set()
        available_networks = []
        networks = result.splitlines()
        for network in networks:
            ssid, signal, bars, security = network.split(":")
            ssid = ssid if ssid else "<Hidden>"  # Handle hidden networks
            if ssid not in seen_networks:
                seen_networks.add(ssid)
                available_networks.append({
                    "ssid": ssid,
                    "signal": signal,
                    "bars": bars,
                    "security": security
                })

        return available_networks

    except subprocess.CalledProcessError as e:
        return {"error": f"Failed to fetch Wi-Fi networks. Error: {e}"}
    except Exception as ex:
        return {"error": f"An unexpected error occurred: {ex}"}
