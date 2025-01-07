import requests
from datetime import datetime, timedelta
from ics import Calendar

from scripts.hfe_logging import configure_logging

logging = configure_logging()


def get_google_calendar_data(url, holiday_url, days=1, forecast=None):
    grouped_events = {}

    try:
        # Fetch the main calendar iCal data
        response = requests.get(url)
        response.raise_for_status()
        cal = Calendar(response.text)

        # Fetch the holiday calendar iCal data
        holiday_response = requests.get(holiday_url)
        holiday_response.raise_for_status()
        holiday_cal = Calendar(holiday_response.text)

        today = datetime.now()
        future_date = today + timedelta(days=days)

        # Process and filter events from both calendars
        for source, calendar_obj in [("Main", cal), ("Holiday", holiday_cal)]:
            for event in sorted(calendar_obj.events, key=lambda e: e.begin):
                # Filter events within the date range
                if today.date() <= event.begin.date() <= future_date.date():
                    event_date = event.begin.date()
                    formatted_date = event_date.strftime("%d %B, %A")
                    date_parts = formatted_date.split(" ")

                    # Use %m and %d for better compatibility
                    forecast_date_key = event_date.strftime("%Y-%m-%d")

                    # Format times (12-hour format with AM/PM)
                    start_time_12hr = event.begin.strftime("%I:%M %p")
                    end_time_12hr = event.end.strftime("%I:%M %p")

                    # Check if the event is all-day
                    is_all_day = (
                        event.begin.time() == datetime.min.time()
                        and event.end.time() == datetime.min.time()
                    )

                    # Group events by formatted date
                    if formatted_date not in grouped_events:
                        grouped_events[formatted_date] = []

                    # Fetch the forecast data if a forecast is provided
                    forecast_data = {}
                    if forecast:
                        # Safely get the data or default to {}
                        forecast_data = forecast.get(forecast_date_key, {})

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
                            "forecast_data": forecast_data,  # store the actual forecast data
                            "source": source,
                        }
                    )

    except requests.exceptions.RequestException as e:
        logging.debug(f"Error fetching calendar data: {e}")

    except Exception as e:
        logging.debug(f"An unexpected error occurred: {e}")

    return grouped_events
