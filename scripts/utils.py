from datetime import datetime


# Function to convert 12-hour clock to 24-hour clock
def convert_to_24_hour(time_str):
    if time_str:
        return datetime.strptime(time_str, "%I:%M %p").strftime("%H:%M")
    return None


def to_milliseconds(value, unit="minutes"):
    """
    Convert a value in minutes or seconds to milliseconds.

    Parameters:
    - value: The numerical value to convert.
    - unit: The unit of the value ('minutes' or 'seconds'). Default is 'minutes'.

    Returns:
    - The value converted to milliseconds.
    """
    if unit == "minutes":
        return value * 60 * 1000
    elif unit == "seconds":
        return value * 1000
    else:
        raise ValueError("Invalid unit. Use 'minutes' or 'seconds'.")
