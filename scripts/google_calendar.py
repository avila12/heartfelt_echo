import requests
from datetime import datetime, timedelta
from ics import Calendar
import pytz

import config
from scripts.hfe_logging import configure_logging
from scripts.utils import safe_round

logging = configure_logging()


def get_google_calendar_data(url, holiday_url, days=1, forecast=None):
    grouped_events = {}

    local_tz = pytz.timezone(config.TIMEZONE)

    try:
        # Fetch the main calendar iCal data
        response = requests.get(url)
        response.raise_for_status()
        cal = Calendar(response.text)

        # Fetch the holiday calendar iCal data
        holiday_response = requests.get(holiday_url)
        holiday_response.raise_for_status()
        holiday_cal = Calendar(holiday_response.text)

        today = datetime.now(tz=local_tz)
        future_date = today + timedelta(days=days)

        # Process and filter events from both calendars
        for source, calendar_obj in [("Main", cal), ("Holiday", holiday_cal)]:
            # Sort events by start time
            for event in sorted(calendar_obj.events, key=lambda e: e.begin):

                # ---- Convert event begin/end to local time ----
                event_start_local = event.begin.astimezone(local_tz)
                event_end_local = event.end.astimezone(local_tz)

                # Filter events within the date range based on local time
                if today.date() <= event_start_local.date() <= future_date.date():
                    # Format date in the style you want
                    formatted_date = event_start_local.strftime("%d %B, %A")
                    date_parts = formatted_date.split(" ")

                    # We'll use the local date key for forecast lookups (Y-m-d)
                    forecast_date_key = event_start_local.strftime("%Y-%m-%d")

                    # Check if the event is all-day by comparing times to 00:00
                    is_all_day = (
                            event_start_local.time() == datetime.min.time()
                            and event_end_local.time() == datetime.min.time()
                    )

                    # Format times (12-hour format with AM/PM)
                    start_time_12hr = event_start_local.strftime("%I:%M %p")
                    end_time_12hr = event_end_local.strftime("%I:%M %p")

                    # Group events by formatted date
                    if formatted_date not in grouped_events:
                        grouped_events[formatted_date] = []

                    # Fetch the forecast data if a forecast is provided
                    forecast_data = forecast.get(forecast_date_key, {}) if forecast else {}

                    if forecast_data:
                        forecast_data["maxtemp_f"] = safe_round(forecast_data.get("maxtemp_f"))
                        forecast_data["mintemp_f"] = safe_round(forecast_data.get("mintemp_f"))

                    grouped_events[formatted_date].append(
                        {
                            "summary": event.name or "Unnamed Event",
                            "description": event.description or "",
                            "location": event.location or "",
                            "start_time": None if is_all_day else start_time_12hr,
                            "end_time": None if is_all_day else end_time_12hr,
                            "date": formatted_date,
                            "forecast_date_key": forecast_date_key,
                            "day": date_parts[0],
                            "month": date_parts[1].strip(","),
                            "weekday": date_parts[2],
                            "is_all_day": is_all_day,
                            "forecast_data": forecast_data,
                            "source": source,
                        }
                    )

    except requests.exceptions.RequestException as e:
        logging.debug(f"Error fetching calendar data: {e}")

    except Exception as e:
        logging.debug(f"An unexpected error occurred: {e}")

    return grouped_events
