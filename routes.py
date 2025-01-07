import os

from flask import Blueprint, render_template, jsonify, request, send_file
from datetime import datetime, timedelta

import config
from scheduler import scheduler
from scripts.google_calendar import get_google_calendar_data
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
routes = Blueprint("routes", __name__)


@routes.before_request
def log_request_info():
    logging.info(f"Request: {request.method} {request.path}")


@routes.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Unhandled exception: {str(e)}")
    return jsonify({"error": "An unexpected error occurred"}), 500


@routes.route("/")
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
        "weather_api_refresh_interval": config.WEATHER_API_REFRESH_INTERVAL,
    }
    get_forecast_data_or_cached(
        zipcode=config.ZIPCODE,
        days=config.FORECAST_DAYS,
        cache_duration=config.CACHE_DURATION,
        weather_data_type="forecast",
    )
    return render_template("index.html", configuration=configuration)


@routes.route("/app/event")
def events():
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    today_date = today.strftime("%d %B, %A")  # Format date like '05 December, Tuesday'
    tomorrow_date = tomorrow.strftime(
        "%d %B, %A"
    )  # Format date like '06 December, Wednesday'
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
        days=7,  # TODO: Make this better
        forecast=three_day_forecast,
    )
    return render_template(
        "events.html",
        today_date=today_date,
        tomorrow_date=tomorrow_date,
        grouped_events=grouped_events,
        forecast=three_day_forecast,
    )


@routes.route("/app/weather")
def weather():
    current_data = get_forecast_cached_data(zipcode="34688", forecast_file="current")
    current_data["condition"]["fa_icon"] = fontawesome_icon(
        code=current_data["condition"]["code"], day=current_data["is_day"]
    )
    return current_data


@routes.route("/app/astronomy")
def astronomy():
    return get_forecast_cached_data(zipcode=config.ZIPCODE, forecast_file="astro")


@routes.route("/app/forecast")
def forecast():
    weather_data_type = request.args.get("weather_data_type", "current")
    return get_forecast_data_or_cached(
        zipcode=config.ZIPCODE,
        days=config.FORECAST_DAYS,
        cache_duration=config.CACHE_DURATION,
        weather_data_type=weather_data_type,
    )


@routes.route("/app/photo")
def get_photo_path():
    try:
        photo_path = photo_cycler.get_next_photo()
        return jsonify({"photo_url": f"/photos/default/{os.path.basename(photo_path)}"})
    except Exception as e:
        routes.logger.error(f"Error in /app/photo: {str(e)}")
        return jsonify({"error": str(e)}), 500


@routes.route("/photos/<path>/<filename>")
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


@routes.route("/set-monitor-state-off")
def set_monitor_state_off():
    set_monitor_state("off")  # Turn off the screen
    return jsonify({"state": "off"}), 200


@routes.route("/set-monitor-state-on")
def set_monitor_state_on():
    set_monitor_state("on_rotate_left")  # Turn on the screen
    return jsonify({"state": "on"}), 200


@routes.route("/show-jobs")
def show_jobs():
    jobs = scheduler.get_jobs()
    return jsonify({"scheduled_jobs": [str(job) for job in jobs]}), 200


@routes.route("/debug-jobs")
def debug_jobs():
    jobs = scheduler.get_jobs()
    return jsonify({"scheduled_jobs": [job.__str__() for job in jobs]}), 200
