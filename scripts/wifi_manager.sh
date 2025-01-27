#!/bin/bash

function connect_to_wifi() {
    local ssid="$1"
    local password="$2"

    # Fetch the list of known networks
    known_networks=$(nmcli -t -f NAME connection show)

    if echo "$known_networks" | grep -q "^${ssid}$"; then
        # If network is known, connect to it
        if nmcli connection up "$ssid"; then
            echo "{\"message\": \"Successfully connected to '$ssid'.\"}"
        else
            echo "{\"error\": \"Failed to connect to '$ssid'.\"}"
        fi
    else
        # If network is not known, try to connect with password
        if nmcli dev wifi connect "$ssid" password "$password"; then
            echo "{\"message\": \"Successfully connected to '$ssid'.\"}"
        else
            echo "{\"error\": \"Failed to connect to '$ssid'.\"}"
        fi
    fi
}

function get_available_wifi() {
    # Rescan for Wi-Fi networks
    if ! nmcli dev wifi rescan; then
        echo "{\"error\": \"Failed to trigger Wi-Fi scan.\"}"
        return
    fi

    sleep 2

    # Get available Wi-Fi networks
    available_networks=$(nmcli -t -f SSID,SIGNAL,BARS,SECURITY dev wifi)

    if [ -z "$available_networks" ]; then
        echo "{\"error\": \"No Wi-Fi networks found.\"}"
        return
    fi

    # Parse unique networks
    echo "$available_networks" | awk -F: '!seen[$1]++ {
        ssid=($1=="") ? "<Hidden>" : $1
        printf "{\"ssid\": \"%s\", \"signal\": \"%s\", \"bars\": \"%s\", \"security\": \"%s\"}\n", ssid, $2, $3, $4
    }'
}

# Main script logic
if [ "$1" == "connect" ]; then
    connect_to_wifi "$2" "$3"
elif [ "$1" == "list" ]; then
    get_available_wifi
else
    echo "Usage:"
    echo "  $0 connect <SSID> <password>    # Connect to a Wi-Fi network"
    echo "  $0 list                        # List available Wi-Fi networks"
fi