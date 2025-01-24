from flask import render_template, request, jsonify, Blueprint
# import subprocess
# import time


# Create blueprint for routes
wifi_bp = Blueprint("wifi_bp", __name__)


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


def connect_to_wifi(ssid, password):
    """
    Connect to a Wi-Fi network using nmcli.
    """
    try:
        known_networks = subprocess.check_output(
            ['nmcli', '-t', '-f', 'NAME', 'connection', 'show']
        ).decode().splitlines()

        if ssid in known_networks:
            subprocess.run(['nmcli', 'connection', 'up', ssid], check=True)
        else:
            subprocess.run(['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password], check=True)

        return {"message": f"Successfully connected to '{ssid}'."}

    except subprocess.CalledProcessError as e:
        return {"error": f"Failed to connect to '{ssid}'. Error: {e}"}
    except Exception as ex:
        return {"error": f"An unexpected error occurred: {ex}"}


@wifi_bp.route('/')
def wifi_index():
    return render_template('wifi.html')


# @wifi_bp.route('/scan', methods=['GET'])
# def scan_networks():
#     networks = get_available_wifi()
#     if 'error' in networks:
#         return jsonify(networks), 500
#     return jsonify(networks)
#
#
# @wifi_bp.route('/connect', methods=['POST'])
# def connect_network():
#     ssid = request.json.get('ssid')
#     password = request.json.get('password')
#
#     if not ssid or not password:
#         return jsonify({"error": "SSID and password are required."}), 400
#
#     response = connect_to_wifi(ssid, password)
#
#     if 'error' in response:
#         return jsonify(response), 500
#     return jsonify(response)