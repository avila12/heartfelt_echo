#!/usr/bin/env python3

import os
import uuid

from flask import Flask, request, render_template, redirect, url_for, flash, Blueprint
import NetworkManager

wifi_bp = Blueprint("main", __name__)
wifi_bp.secret_key = "1234"  # testing only will move to env after


def get_wifi_device():
    """Return the first Wi-Fi device managed by NetworkManager or None if not found."""
    for dev in NetworkManager.NetworkManager.GetDevices():
        if dev.DeviceType == NetworkManager.NM_DEVICE_TYPE_WIFI:
            return dev
    return None


def get_current_connection():
    """
    Return (connection_id, ssid) of currently active Wi-Fi, or (None, None) if none active.
    """
    for c in NetworkManager.NetworkManager.ActiveConnections:
        if c.Connection.GetSettings().get('connection', {}).get('type') == '802-11-wireless':
            conn_id = c.Connection.GetSettings()['connection']['id']
            ssid = c.Connection.GetSettings()['802-11-wireless']['ssid'].decode("utf-8", "ignore")
            return conn_id, ssid
    return None, None


def list_saved_connections():
    """
    Return a list of (connection_id, ssid) for all Wi-Fi connections saved in NetworkManager.
    """
    results = []
    for c in NetworkManager.Settings.ListConnections():
        settings = c.GetSettings()
        if settings.get('connection', {}).get('type') == '802-11-wireless':
            conn_id = settings['connection']['id']
            ssid_bytes = settings['802-11-wireless'].get('ssid', b'')
            ssid = ssid_bytes.decode("utf-8", "ignore")
            results.append((conn_id, ssid))
    return results


def create_or_update_wifi(ssid, password, connection_id=None):
    """
    Create or update a Wi-Fi connection in NetworkManager with the given SSID and password.
    """
    if not connection_id:
        connection_id = f"WiFi-{ssid}"

    new_connection = {
        "connection": {
            "id": connection_id,
            "type": "802-11-wireless",
            "uuid": str(uuid.uuid4()),
        },
        "802-11-wireless": {
            "ssid": ssid.encode("utf-8"),
            "mode": "infrastructure",
            "security": "802-11-wireless-security",
        },
        "802-11-wireless-security": {
            "key-mgmt": "wpa-psk",
            "psk": password,
        },
        "ipv4": {"method": "auto"},
        "ipv6": {"method": "auto"},
    }

    # Check if the connection already exists
    existing = None
    for c in NetworkManager.Settings.ListConnections():
        s = c.GetSettings()
        if s['connection']['id'] == connection_id:
            existing = c
            break

    if existing:
        existing.Update(new_connection)
        return f"Updated existing connection '{connection_id}'."
    else:
        NetworkManager.Settings.AddConnection(new_connection)
        return f"Created new connection '{connection_id}'."


def activate_wifi(connection_id):
    """Activate (connect to) a saved Wi-Fi connection by its connection ID."""
    wifi_dev = get_wifi_device()
    if not wifi_dev:
        raise RuntimeError("No Wi-Fi device found or Wi-Fi not managed by NetworkManager.")

    # Find the connection
    target_connection = None
    for c in NetworkManager.Settings.ListConnections():
        s = c.GetSettings()
        if s['connection']['id'] == connection_id:
            target_connection = c
            break

    if not target_connection:
        raise RuntimeError(f"No connection with ID '{connection_id}' found.")

    NetworkManager.NetworkManager.ActivateConnection(target_connection, wifi_dev, "/")


def remove_wifi(connection_id):
    """
    Remove a Wi-Fi connection from NetworkManager’s saved connections.
    (Does not necessarily disconnect if currently connected.)
    """
    for c in NetworkManager.Settings.ListConnections():
        s = c.GetSettings()
        if s['connection']['id'] == connection_id:
            c.Delete()
            return f"Removed connection '{connection_id}'"
    return f"No connection '{connection_id}' found."


@wifi_bp.route('/')
def index():
    """
    Main page: show currently connected Wi-Fi, all saved Wi-Fi connections,
    and links to add or remove connections.
    """
    current_conn_id, current_ssid = get_current_connection()
    saved_conns = list_saved_connections()
    return render_template(
        'index.html',
        current_conn_id=current_conn_id,
        current_ssid=current_ssid,
        saved_conns=saved_conns
    )


@wifi_bp.route('/add', methods=['GET', 'POST'])
def add():
    """
    GET: Show a form to add a Wi-Fi network (SSID, password, optional connection ID).
    POST: Create or update that Wi-Fi network in NetworkManager, then activate it.
    """
    if request.method == 'POST':
        ssid = request.form.get('ssid', '').strip()
        password = request.form.get('password', '').strip()
        connection_id = request.form.get('connection_id', '').strip() or None

        if not ssid or not password:
            flash("SSID and password are required.", "error")
            return redirect(url_for('add'))

        msg = create_or_update_wifi(ssid, password, connection_id)
        flash(msg, "info")

        # Now attempt to activate
        actual_id = connection_id or f"WiFi-{ssid}"
        try:
            activate_wifi(actual_id)
            flash(f"Activating connection '{actual_id}'...", "info")
        except Exception as e:
            flash(f"Failed to activate: {e}", "error")

        return redirect(url_for('index'))
    else:
        return render_template('add.html')


@wifi_bp.route('/remove', methods=['GET', 'POST'])
def remove():
    """
    GET: Show a form that lists all saved Wi-Fi networks with a remove button.
    POST: Remove the selected Wi-Fi connection from NetworkManager.
    """
    if request.method == 'POST':
        connection_id = request.form.get('connection_id', '').strip()
        if connection_id:
            msg = remove_wifi(connection_id)
            flash(msg, "info")
        else:
            flash("No connection ID provided.", "error")
        return redirect(url_for('remove'))
    else:
        # show a list of all saved Wi-Fi connections
        saved_conns = list_saved_connections()
        return render_template('remove.html', saved_conns=saved_conns)


@wifi_bp.route('/status')
def status():
    """
    Simple API-like endpoint returning current Wi-Fi status (connected SSID or not).
    """
    conn_id, ssid = get_current_connection()
    if conn_id:
        return {
            "connected": True,
            "connection_id": conn_id,
            "ssid": ssid
        }
    else:
        return {
            "connected": False,
            "connection_id": None,
            "ssid": None
        }
