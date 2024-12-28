import os
from flask import Flask, render_template, jsonify, request, send_file, url_for
from dotenv import load_dotenv
from datetime import datetime, timedelta

from google_calendar import get_google_calendar_data
from photo import photo_cycler
from weatherapi import (
    get_forecast_data_or_cached,
    get_forecast_cached_data,
    fontawesome_icon,
)

load_dotenv()

app = Flask(__name__)

zipcode = os.getenv('zipcode', '33615')

@app.route("/")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"


@app.route("/test")
def index():
    configuration = {
        # base routes
        "route": os.getenv('route', "/app"),

        # time
        "timeFormat": int(os.getenv("timeFormat", 12)),
        "dateFormat": os.getenv("dateFormat", "MMMM D"),
        "clockType": os.getenv("clockType", "digital"),
        "timezone": os.getenv("timezone", "America/New_York"),
        "showSeconds": int(os.getenv("showSeconds", 1)),
        "showAmpm": int(os.getenv("showAmpm", 1)),
        "time_refresh": int(os.getenv("time_refresh", 1000)),

        # weather
        "weather_route": os.getenv("weather_route", "app/weather"),
        "latitude": os.getenv("latitude", "28.0781"),
        "longitude": os.getenv("longitude", "-82.7637"),
        "weather_refresh": int(os.getenv("weather_refresh", 900000)),

        # astronomy setup
        "astronomy_route": os.getenv("astronomy_route", "app/astronomy"),
        "astronomy_refresh": int(os.getenv("astronomy_refresh", 900000)),

        # events setup
        "event_route": os.getenv("event_route", "app/event"),
        "event_refresh": int(os.getenv("event_refresh", 900000)),

        # photo setup
        "photo_route": os.getenv("photo_route", "app/photo"),
        "photo_transition": int(os.getenv("photo_transition", 1)),  # true/false
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
    if not event_url:
        return ""
    if not event_holiday_url:
        return ""

    grouped_events = get_google_calendar_data(url=event_url, holiday_url=event_holiday_url, days=7, forcast=three_day_forecast)
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
        zipcode=zipcode, days=app.config.get("forcast_days", 3), cache_duration=app.config.get("forcast_cache_duration", 900), file_type=file
    )

@app.route("/app/photo")
def get_photo_path():
    try:
        photo_path = photo_cycler.get_next_photo()
        # Generate URL pointing to the /photos/ path served by Nginx
        return jsonify(
            {
                "photo_url": f"/photos/{os.path.basename(photo_path)}"
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Optional: Keep this route for development when Nginx is not used
@app.route("/serve-photos")
def serve_photo(filename):
    try:
        # Locate the photo in today's directory or default list
        all_photos = photo_cycler.photos
        for photo in all_photos:
            return send_file(photo)
        return jsonify({"error": "File not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
