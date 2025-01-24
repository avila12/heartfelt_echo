import subprocess
import time


def get_available_wifi():
    """
    Fetch and display all available Wi-Fi networks using nmcli, ensuring a fresh scan,
    and eliminate duplicate SSIDs from the output.
    """
    try:
        # Check if `nmcli` is installed
        subprocess.run(['nmcli', '--version'], check=True, stdout=subprocess.DEVNULL)
    except FileNotFoundError:
        print("Error: `nmcli` is not installed. Install it using `sudo apt install network-manager`.")
        return

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
        networks = result.splitlines()
        for network in networks:
            ssid, signal, bars, security = network.split(":")
            ssid = ssid if ssid else "<Hidden>"  # Handle hidden networks
            if ssid not in seen_networks:
                seen_networks.add(ssid)
                print(f"{ssid:<25} {signal:<10} {bars:<10} {security:<10}")

        print("-" * 50)

    except subprocess.CalledProcessError as e:
        print(f"Failed to fetch Wi-Fi networks. Error: {e}")
    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")


if __name__ == "__main__":
    try:
        get_available_wifi()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")