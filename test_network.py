import subprocess


def connect_to_wifi(ssid, password):
    """
    Connect to a Wi-Fi network using NetworkManager.
    """
    try:
        # Check if the network is already known
        known_networks = subprocess.check_output(
            ['nmcli', '-t', '-f', 'SSID', 'connection', 'show']).decode().splitlines()

        if ssid in known_networks:
            print(f"Network '{ssid}' already known. Connecting...")
            subprocess.run(['nmcli', 'connection', 'up', ssid], check=True)
        else:
            print(f"Network '{ssid}' not known. Adding and connecting...")
            # Add and connect to a new Wi-Fi network
            subprocess.run(['nmcli', 'dev', 'wifi', 'connect', ssid, 'password', password], check=True)

        print(f"Successfully connected to '{ssid}'.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to connect to '{ssid}'. Error: {e}")
    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")


if __name__ == "__main__":
    # Replace these with your desired network credentials
    network_ssid = input("Enter the Wi-Fi SSID: ")
    network_password = input("Enter the Wi-Fi password: ")

    connect_to_wifi(network_ssid, network_password)