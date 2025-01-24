import subprocess
import time


def get_available_wifi():
    """
    Fetch and display all available Wi-Fi networks using nmcli,
    and return the list of unique SSIDs.
    """
    try:
        # Trigger a Wi-Fi scan
        print("Scanning for available Wi-Fi networks...")
        subprocess.run(['nmcli', 'dev', 'wifi', 'rescan'], check=True)

        # Allow time for the scan to complete
        time.sleep(2)

        # Get available Wi-Fi networks
        result = subprocess.check_output(['nmcli', '-t', '-f', 'SSID,SIGNAL,BARS,SECURITY', 'dev', 'wifi']).decode()

        print("\nAvailable Wi-Fi Networks:")
        print("-" * 50)
        print(f"{'SSID':<25} {'Signal':<10} {'Bars':<10} {'Security':<10}")
        print("-" * 50)

        # Parse and eliminate duplicate networks
        seen_networks = set()  # Use a set to store unique SSIDs
        available_networks = []
        networks = result.splitlines()
        for network in networks:
            ssid, signal, bars, security = network.split(":")
            ssid = ssid if ssid else "<Hidden>"  # Handle hidden networks
            if ssid not in seen_networks:
                seen_networks.add(ssid)
                available_networks.append(ssid)
                print(f"{ssid:<25} {signal:<10} {bars:<10} {security:<10}")

        print("-" * 50)
        return available_networks

    except subprocess.CalledProcessError as e:
        print(f"Failed to fetch Wi-Fi networks. Error: {e}")
    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")
        return []


def connect_to_wifi(ssid, password):
    """
    Connect to a Wi-Fi network using nmcli.
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
    try:
        # Get the list of available networks
        networks = get_available_wifi()

        if networks:
            # Ask the user to choose a network
            print("\nAvailable Networks:")
            for i, network in enumerate(networks, start=1):
                print(f"{i}. {network}")

            choice = int(input("\nEnter the number of the network you want to connect to: "))
            if 1 <= choice <= len(networks):
                selected_ssid = networks[choice - 1]
                if selected_ssid == "<Hidden>":
                    print("Cannot connect to hidden networks through this script.")
                else:
                    wifi_password = input(f"Enter the password for '{selected_ssid}': ")
                    connect_to_wifi(selected_ssid, wifi_password)
            else:
                print("Invalid choice. Exiting.")
        else:
            print("No networks available to connect to.")

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")