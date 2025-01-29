from flask import render_template, request, jsonify, Blueprint

from scripts.wifi_connector import get_available_wifi, connect_to_wifi

# Create blueprint for routes
wifi_bp = Blueprint("wifi_bp", __name__)

@wifi_bp.route('/')
def wifi_index():
    return render_template('wifi.html')


@wifi_bp.route('/scan', methods=['GET'])
def scan_networks():
    networks = get_available_wifi()

    if 'error' in networks:
        return jsonify(networks), 500
    return jsonify(networks)


@wifi_bp.route('/connect', methods=['POST'])
def connect_network():
    ssid = request.json.get('ssid')
    password = request.json.get('password')

    if not ssid or not password:
        return jsonify({"error": "SSID and password are required."}), 400

    response = connect_to_wifi(ssid, password)

    if 'error' in response:
        return jsonify(response), 500
    return jsonify(response)
