import subprocess

from scripts.hfe_logging import configure_logging

logging = configure_logging()


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
            subprocess.run(
                ["xrandr", "--output", "HDMI-1", "--auto", "--rotate", "left"],
                check=True,
            )
        else:
            logging.debug(f"Unknown state: {state}")
    except subprocess.CalledProcessError as e:
        logging.debug(f"Failed to set monitor state to '{state}': {e}")
