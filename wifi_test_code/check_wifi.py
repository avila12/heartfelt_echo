import subprocess

def check_wifi_status():
    """
    Check the current Wi-Fi connection status using nmcli.
    """
    try:
        # Get the Wi-Fi connection status
        result = subprocess.check_output(['nmcli', '-t', '-f', 'ACTIVE,SSID,SIGNAL', 'dev', 'wifi'], text=True)
        active_networks = [line for line in result.splitlines() if line.startswith("yes")]

        if active_networks:
            for network in active_networks:
                _, ssid, signal = network.split(':')
                print(f"Connected to SSID: {ssid}")
                print(f"Signal Strength: {signal}%")
        else:
            print("Not connected to any Wi-Fi network.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to get Wi-Fi status. Error: {e}")
    except FileNotFoundError:
        print("nmcli is not installed. Install it using 'sudo apt install network-manager'.")
    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")

if __name__ == "__main__":
    check_wifi_status()