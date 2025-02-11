import os
import subprocess

from flask import Blueprint, render_template, jsonify, request, send_file
from datetime import datetime, timedelta

import config
from scheduler import scheduler
from scripts.google_calendar2 import get_google_calendar_data
from scripts.monitor_control import set_monitor_state
from scripts.photo import photo_cycler
from scripts.weatherapi import (
    get_forecast_data_or_cached,
    get_forecast_cached_data,
    fontawesome_icon,
)
from scripts.hfe_logging import configure_logging

logging = configure_logging()

# Create blueprint for routes
main_bp = Blueprint("main", __name__)


@main_bp.before_request
def log_request_info():
    logging.info(f"Request: {request.method} {request.path}")


@main_bp.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Unhandled exception: {str(e)}")
    return jsonify({"error": "An unexpected error occurred"}), 500


@main_bp.route("/")
def index():
    configuration = {
        # Time configurations
        "timeFormat": config.TIME_FORMAT,
        "dateFormat": config.DATE_FORMAT,
        "clockType": config.CLOCK_TYPE,
        "timezone": config.TIMEZONE,
        "showSeconds": config.SHOW_SECONDS,
        "showAmpm": config.SHOW_AM_PM,
        "time_refresh": config.TIME_REFRESH,
        # Weather configurations
        "weather_route": config.WEATHER_ROUTE,
        "latitude": config.LATITUDE,
        "longitude": config.LONGITUDE,
        "weather_refresh": config.WEATHER_REFRESH,
        # Astronomy configurations
        "astronomy_route": config.ASTRONOMY_ROUTE,
        "astronomy_refresh": config.ASTRONOMY_REFRESH,
        # Events configurations
        "event_route": config.EVENT_ROUTE,
        "event_refresh": config.EVENT_REFRESH,
        # Photo configurations
        "photo_route": config.PHOTO_ROUTE,
        "photo_transition": config.PHOTO_TRANSITION,
        "photo_refresh_interval": config.PHOTO_REFRESH_INTERVAL,
        "photo_fade_duration": config.PHOTO_FADE_DURATION,
        # forcast configurations
        "weather_api_route": config.WEATHER_API_ROUTE,
        "weather_api_refresh": config.WEATHER_API_REFRESH,
    }
    # update weather data before html loads
    get_forecast_data_or_cached(
        zipcode=config.ZIPCODE,
        days=config.FORECAST_DAYS,
        cache_duration=config.WEATHER_API_CACHE_DURATION,
        weather_data_type="forecast",
    )
    return render_template("index.html", configuration=configuration)


@main_bp.route("/app/event")
def events():
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    today_date = today.strftime("%d %B, %A")
    tomorrow_date = tomorrow.strftime("%d %B, %A")
    three_day_forecast = get_forecast_cached_data(
        zipcode=config.ZIPCODE, forecast_file="forecast"
    )

    event_url = config.EVENT_URL
    event_holiday_url = config.EVENT_HOLIDAY_URL
    if not event_url or not event_holiday_url:
        return ""

    grouped_events = get_google_calendar_data(
        url=event_url,
        holiday_url=event_holiday_url,
        days=7,
        forecast=three_day_forecast,
    )

    # Sort events by start time for each day
    # need to move this in function
    for day, events in grouped_events.items():
        grouped_events[day] = sorted(
            events,
            key=lambda event: (
                datetime.strptime(event["start_time"], "%I:%M %p")
                if event["start_time"]
                else datetime.min
            ),
        )

    return render_template(
        "events.html",
        today_date=today_date,
        tomorrow_date=tomorrow_date,
        grouped_events=grouped_events,
        forecast=three_day_forecast,
    )


@main_bp.route("/app/weather")
def weather():
    current_data = get_forecast_cached_data(zipcode="34688", forecast_file="current")
    current_data["condition"]["fa_icon"] = fontawesome_icon(
        code=current_data["condition"]["code"], day=current_data["is_day"]
    )
    return current_data


@main_bp.route("/app/astronomy")
def astronomy():
    return get_forecast_cached_data(zipcode=config.ZIPCODE, forecast_file="astro")


@main_bp.route("/app/weather-api")
def weather_api():
    weather_data_type = request.args.get("weather_data_type", "current")
    return get_forecast_data_or_cached(
        zipcode=config.ZIPCODE,
        days=config.FORECAST_DAYS,
        cache_duration=config.WEATHER_API_CACHE_DURATION,
        weather_data_type=weather_data_type,
    )


@main_bp.route("/app/photo")
def get_photo_path():
    try:
        photo_path = photo_cycler.get_next_photo()
        return jsonify({"photo_url": f"/photos/default/{os.path.basename(photo_path)}"})
    except Exception as e:
        main_bp.logger.error(f"Error in /app/photo: {str(e)}")
        return jsonify({"error": str(e)}), 500


@main_bp.route("/photos/<path>/<filename>")
def serve_photo(path, filename):
    try:
        # Securely construct the file path
        file_path = os.path.join("photos", path, filename)
        # Verify the file exists
        if not os.path.isfile(file_path):
            return jsonify({"error": "File not found"}), 404
        return send_file(file_path)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@main_bp.route("/set-monitor-state-off")
def set_monitor_state_off():
    set_monitor_state("off")  # Turn off the screen
    return jsonify({"state": "off"}), 200


@main_bp.route("/set-monitor-state-on")
def set_monitor_state_on():
    set_monitor_state("on_rotate_left")  # Turn on the screen
    return jsonify({"state": "on"}), 200


# UTIL END POINTS MAYBE MOVE TO ADMIN


@main_bp.route("/show-jobs")
def show_jobs():
    jobs = scheduler.get_jobs()
    return jsonify({"scheduled_jobs": [str(job) for job in jobs]}), 200


@main_bp.route("/debug-jobs")
def debug_jobs():
    jobs = scheduler.get_jobs()
    return jsonify({"scheduled_jobs": [job.__str__() for job in jobs]}), 200


@main_bp.route('/pull', methods=['POST'])
def pull_repo():
    """
    Endpoint to pull the latest changes from GitHub.
    You might want to protect this route with some
    form of authentication or a secret token.
    """
    # Path to your local git repository
    repo_path = "/home/pi/heartfelt_echo"

    # Run 'sudo git pull' in that directory
    result = subprocess.run(["sudo", "git", "pull"], cwd=repo_path, capture_output=True, text=True)

    # Return the output for debugging/confirmation
    if result.returncode == 0:
        return f"Git pull successful:\n{result.stdout}", 200
    else:
        return f"Git pull failed:\n{result.stderr}", 500


@main_bp.route('/reboot', methods=['POST'])
def reboot_pi():
    """
    Endpoint to reboot the Raspberry Pi.
    Again, consider adding authentication or restricting access.
    """
    # Run 'sudo reboot'
    subprocess.Popen(["sudo", "reboot"])
    return "Reboot command issued. The system will go down shortly.", 200


