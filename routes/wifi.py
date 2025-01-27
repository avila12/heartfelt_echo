from flask import render_template, request, jsonify, Blueprint

import subprocess

script_path = "./home/pi/heartfelt_echo/scripts/wifi_manager.sh"

# Create blueprint for routes
wifi_bp = Blueprint("wifi_bp", __name__)

@wifi_bp.route('/')
def wifi_index():
    return render_template('wifi.html')


@wifi_bp.route('/scan', methods=['GET'])
def scan_networks():
    # networks = get_available_wifi()

    networks = subprocess.run([script_path, "list"], capture_output=True, text=True)

    if 'error' in networks:
        return jsonify(networks), 500
    return jsonify(networks)


@wifi_bp.route('/connect', methods=['POST'])
def connect_network():
    ssid = request.json.get('ssid')
    password = request.json.get('password')

    if not ssid or not password:
        return jsonify({"error": "SSID and password are required."}), 400

    response = subprocess.run([script_path, "connect", ssid, password], capture_output=True, text=True)

    if 'error' in response:
        return jsonify(response), 500
    return jsonify(response)
