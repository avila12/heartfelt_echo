import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration variables
os.environ["DISPLAY"] = ":0"

MONITOR_WAKE = os.getenv("MONITOR_WAKE", None)
MONITOR_SLEEP = os.getenv("MONITOR_SLEEP", None)


# Flask configurations
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))

# Timezone and format configurations
TIME_FORMAT = int(os.getenv("TIME_FORMAT", 12))
DATE_FORMAT = os.getenv("DATE_FORMAT", "MMMM D")
CLOCK_TYPE = os.getenv("CLOCK_TYPE", "digital")
TIMEZONE = os.getenv("timezone", "America/New_York")
SHOW_SECONDS = int(os.getenv("showSeconds", 1))
SHOW_AM_PM = int(os.getenv("SHOW_AM_PM", 1))
TIME_REFRESH = int(os.getenv("TIME_REFRESH", 1000))

# Weather configurations
WEATHER_ROUTE = "app/weather"
WEATHERAPI_KEY = os.getenv("WEATHERAPI_KEY", "")
WEATHER_REFRESH = int(os.getenv("WEATHER_REFRESH", 900000))
LATITUDE = os.getenv("LATITUDE", "28.0781")
LONGITUDE = os.getenv("LONGITUDE", "-82.7637")
ZIPCODE = os.getenv("zipcode", "33615")

# Astronomy configurations
ASTRONOMY_ROUTE = "app/astronomy"
ASTRONOMY_REFRESH = int(os.getenv("ASTRONOMY_REFRESH", 900000))

# Events configurations
EVENT_ROUTE = "app/event"
EVENT_REFRESH = int(os.getenv("EVENT_REFRESH", 900000))
EVENT_URL = os.getenv("EVENT_URL", "")
EVENT_HOLIDAY_URL = os.getenv("EVENT_HOLIDAY_URL", "")

# Photo configurations
PHOTO_ROUTE = "app/photo"
PHOTO_TRANSITION = int(os.getenv("PHOTO_TRANSITION", 1))
PHOTO_REFRESH_INTERVAL = int(os.getenv("PHOTO_REFRESH_INTERVAL", 120000))
PHOTO_FADE_DURATION = int(os.getenv("PHOTO_FADE_DURATION", 1000))

# Forecat
FORECAST_DAYS = int(os.getenv("FORECAST_DAYS", 3))
CACHE_DURATION = int(os.getenv("FORECAST_CACHE_DURATION", 900))