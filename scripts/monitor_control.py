import subprocess
import logging
logging.basicConfig(
    filename='flask.log',  # Log file
    level=logging.DEBUG,  # Log level
    format='%(asctime)s %(levelname)s: %(message)s'
)

def set_monitor_state(state):
    """
    Controls the monitor state using xrandr.
    :param state: "off", "on_rotate_left"
    """
    logging.debug(f"Setting monitor state to: {state}")
    try:
        if state == "off":
            subprocess.run(["xrandr", "--output", "HDMI-1", "--off"], check=True)
        elif state == "on_rotate_left":
            subprocess.run(["xrandr", "--output", "HDMI-1", "--auto", "--rotate", "left"], check=True)
        else:
            print(f"Unknown state: {state}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to set monitor state to '{state}': {e}")