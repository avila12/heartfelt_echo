from datetime import datetime


# Function to convert 12-hour clock to 24-hour clock
def convert_to_24_hour(time_str):
    if time_str:
        return datetime.strptime(time_str, "%I:%M %p").strftime("%H:%M")
    return None
