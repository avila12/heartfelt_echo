import requests
from datetime import datetime, timedelta
from ics import Calendar


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
        for source, calendar in [("Main", cal), ("Holiday", holiday_cal)]:
            for event in sorted(calendar.events, key=lambda e: e.begin):
                # Filter events within the date range
                if today.date() <= event.begin.date() <= future_date.date():
                    event_date = event.begin.date()
                    formatted_date = event_date.strftime("%d %B, %A")
                    date_parts = formatted_date.split(" ")
                    forecast_date_key = event_date.strftime("%Y-%-m-%-d")

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

                    if forecast:
                        try:
                            forcast_data = forecast[forecast_date_key]
                        except Exception as e:
                            forecast_data = {}
                    else:
                        forecast_data = {}

                    grouped_events[formatted_date].append(
                        {
                            "summary": event.name or "Unnamed Event",
                            "start_time": start_time_12hr if not is_all_day else None,
                            "end_time": end_time_12hr if not is_all_day else None,
                            "date": formatted_date,
                            "forecast_date_key": forecast_date_key,
                            "day": date_parts[0],
                            "month": date_parts[1].strip(","),
                            "weekday": date_parts[2],
                            "is_all_day": is_all_day,
                            "forecast_data": forecast_data,
                            "source": source,  # Indicate whether event is from Main or Holiday calendar
                        }
                    )

    except requests.exceptions.RequestException as e:
        print(f"Error fetching calendar data: {e}")  # Consider logging this instead

    except Exception as e:
        print(f"An unexpected error occurred: {e}")  # Consider logging this instead

    return grouped_events
