import os
from flask import Flask, render_template, jsonify, request, send_file
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from datetime import datetime, timedelta
import atexit
import logging

# Import custom scripts
from scripts.google_calendar import get_google_calendar_data
from scripts.photo import photo_cycler
from scripts.monitor_control import set_monitor_state
from scripts.utils import convert_to_24_hour
from scripts.weatherapi import (
    get_forecast_data_or_cached,
    get_forecast_cached_data,
    fontawesome_icon,
)

# Load environment variables
load_dotenv()
os.environ["DISPLAY"] = ":0"

# Logging setup
logging.basicConfig(level=logging.INFO)
logging.getLogger("apscheduler").setLevel(logging.DEBUG)

monitor_wake_time = os.getenv("MONITOR_WAKE", None)
monitor_sleep_time = os.getenv("MONITOR_SLEEP", None)

scheduler = BackgroundScheduler()

# Add jobs
if monitor_wake_time:
    monitor_wake_time_24hr = convert_to_24_hour(monitor_wake_time)
    wake_hour, wake_minute = map(int, monitor_wake_time_24hr.split(':'))
    scheduler.add_job(
        lambda: set_monitor_state("on_rotate_left"),
        'cron',
        hour=wake_hour,
        minute=wake_minute,
        misfire_grace_time=60,
        id="monitor_on_job"
    )

if monitor_sleep_time:
    sleep_time_24hr = convert_to_24_hour(monitor_sleep_time)
    sleep_hour, sleep_minute = map(int, sleep_time_24hr.split(':'))
    scheduler.add_job(
        lambda: set_monitor_state("off"),
        'cron',
        hour=sleep_hour,
        minute=sleep_minute,
        misfire_grace_time=60,
        id="monitor_off_job"
    )

scheduler.start()
atexit.register(lambda: scheduler.shutdown())

# Flask app
app = Flask(__name__)

# Default ZIP code
zipcode = os.getenv('zipcode', '33615')

# Routes
@app.route("/")
def index():
    configuration = {
        # Time configurations
        "timeFormat": int(os.getenv("timeFormat", 12)),
        "dateFormat": os.getenv("dateFormat", "MMMM D"),
        "clockType": os.getenv("clockType", "digital"),
        "timezone": os.getenv("timezone", "America/New_York"),
        "showSeconds": int(os.getenv("showSeconds", 1)),
        "showAmpm": int(os.getenv("showAmpm", 1)),
        "time_refresh": int(os.getenv("time_refresh", 1000)),

        # Weather configurations
        "weather_route": os.getenv("weather_route", "app/weather"),
        "latitude": os.getenv("latitude", "28.0781"),
        "longitude": os.getenv("longitude", "-82.7637"),
        "weather_refresh": int(os.getenv("weather_refresh", 900000)),

        # Astronomy configurations
        "astronomy_route": os.getenv("astronomy_route", "app/astronomy"),
        "astronomy_refresh": int(os.getenv("astronomy_refresh", 900000)),

        # Events configurations
        "event_route": os.getenv("event_route", "app/event"),
        "event_refresh": int(os.getenv("event_refresh", 900000)),

        # Photo configurations
        "photo_route": os.getenv("photo_route", "app/photo"),
        "photo_transition": int(os.getenv("photo_transition", 1)),
        "photo_refresh_interval": int(os.getenv("photo_refresh_interval", 120000)),
        "photo_fade_duration": int(os.getenv("photo_fade_duration", 1000)),
    }
    get_forecast_data_or_cached()
    return render_template("index.html", configuration=configuration)

@app.route("/app/event")
def events():
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    today_date = today.strftime("%d %B, %A")  # Format date like '05 December, Tuesday'
    tomorrow_date = tomorrow.strftime(
        "%d %B, %A"
    )  # Format date like '06 December, Wednesday'
    three_day_forecast = get_forecast_cached_data(
        zipcode=zipcode, forecast_file="forecast"
    )

    event_url = os.getenv("event_url")
    event_holiday_url = os.getenv("event_holiday_url")
    if not event_url or not event_holiday_url:
        return ""

    grouped_events = get_google_calendar_data(
        url=event_url, holiday_url=event_holiday_url, days=7, forcast=three_day_forecast
    )
    return render_template(
        "events.html",
        today_date=today_date,
        tomorrow_date=tomorrow_date,
        grouped_events=grouped_events,
        forecast=three_day_forecast,
    )

@app.route("/app/weather")
def weather():
    current_data = get_forecast_cached_data(zipcode="34688", forecast_file="current")
    current_data["condition"]["fa_icon"] = fontawesome_icon(
        code=current_data["condition"]["code"], day=current_data["is_day"]
    )
    return current_data

@app.route("/app/astronomy")
def astronomy():
    return get_forecast_cached_data(zipcode=zipcode, forecast_file="astro")

@app.route("/app/forcast")
def forcast():
    file = request.args.get("file", "current")
    return get_forecast_data_or_cached(
        zipcode=zipcode,
        days=int(os.getenv("forcast_days", 3)),
        cache_duration=int(os.getenv("forcast_cache_duration", 900)),
        file_type=file,
    )

@app.route("/app/photo")
def get_photo_path():
    try:
        photo_path = photo_cycler.get_next_photo()
        return jsonify({"photo_url": f"/photos/default/{os.path.basename(photo_path)}"})
    except Exception as e:
        app.logger.error(f"Error in /app/photo: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/serve-photos")
def serve_photo(filename):
    try:
        all_photos = photo_cycler.photos
        for photo in all_photos:
            return send_file(photo)
        return jsonify({"error": "File not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/set-monitor-state-off")
def set_monitor_state_off():
    set_monitor_state("off")  # Turn off the screen
    return jsonify({"state": "off"}), 200

@app.route("/set-monitor-state-on")
def set_monitor_state_on():
    set_monitor_state("on_rotate_left")  # Turn on the screen
    return jsonify({"state": "on"}), 200

@app.route("/show-jobs")
def show_jobs():
    jobs = scheduler.get_jobs()
    return jsonify({"scheduled_jobs": [str(job) for job in jobs]}), 200

@app.route("/debug-jobs")
def debug_jobs():
    jobs = scheduler.get_jobs()
    return jsonify({"scheduled_jobs": [job.__str__() for job in jobs]}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
