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

        # We'll gather *all* events (from both calendars) in a flat list
        # so we can later figure out which one is "next" chronologically.
        all_events = []

        # Process and filter events from both calendars
        for source, calendar_obj in [("Main", cal), ("Holiday", holiday_cal)]:
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

                    # Fetch the forecast data if a forecast is provided
                    forecast_data = (
                        forecast.get(forecast_date_key, {}) if forecast else {}
                    )
                    if forecast_data:
                        forecast_data["maxtemp_f"] = safe_round(
                            forecast_data.get("maxtemp_f")
                        )
                        forecast_data["mintemp_f"] = safe_round(
                            forecast_data.get("mintemp_f")
                        )

                    # Build the event dictionary (including the actual datetime for sorting)
                    event_dict = {
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
                        # We'll add a placeholder for this flag, default False
                        "is_next_event": False,
                        # Keep the actual datetime object for logic after we gather all events
                        "_start_datetime_obj": event_start_local,
                    }

                    # Add to our flat list of events
                    all_events.append(event_dict)

        # --- Determine which event is next based on the current time ---
        # 1. Filter out events that have already started (start < now).
        upcoming_events = [e for e in all_events if e["_start_datetime_obj"] >= today]

        # 2. Sort by start time
        upcoming_events.sort(key=lambda e: e["_start_datetime_obj"])

        # 3. If there's at least one upcoming event, mark the first one as next
        if upcoming_events:
            upcoming_events[0]["is_next_event"] = True

        # --- Now group the events by their formatted_date for final return ---
        grouped_events = {}
        for e in all_events:
            formatted_date = e["date"]  # same as what we used above
            if formatted_date not in grouped_events:
                grouped_events[formatted_date] = []
            # Remove the private _start_datetime_obj from the final dict
            copy_for_output = {k: v for k, v in e.items() if k != "_start_datetime_obj"}
            grouped_events[formatted_date].append(copy_for_output)

    except requests.exceptions.RequestException as e:
        logging.debug(f"Error fetching calendar data: {e}")

    except Exception as e:
        logging.debug(f"An unexpected error occurred: {e}")

    return grouped_events
