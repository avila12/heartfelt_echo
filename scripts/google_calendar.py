import requests
from datetime import datetime, timedelta, time
import pytz
import recurring_ical_events
from icalendar import Calendar

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
        main_calendar = Calendar.from_ical(response.text)

        # Fetch the holiday calendar iCal data
        holiday_response = requests.get(holiday_url)
        holiday_response.raise_for_status()
        holiday_calendar = Calendar.from_ical(holiday_response.text)

        today = datetime.now(tz=local_tz)
        future_date = today + timedelta(days=days)

        # Gather all events
        all_events = []

        # Process and filter events from both calendars
        for source, calendar_obj in [
            ("Main", main_calendar),
            ("Holiday", holiday_calendar),
        ]:
            for event in recurring_ical_events.of(calendar_obj).between(
                today, future_date
            ):
                event_start = event.get("DTSTART").dt
                event_end = event.get("DTEND").dt if "DTEND" in event else None

                # Handle all-day events
                if isinstance(event_start, datetime):
                    event_start_local = event_start.astimezone(local_tz)
                else:
                    event_start_local = local_tz.localize(
                        datetime.combine(event_start, time.min)
                    )

                if event_end:
                    if isinstance(event_end, datetime):
                        event_end_local = event_end.astimezone(local_tz)
                    else:
                        event_end_local = local_tz.localize(
                            datetime.combine(event_end, time.min)
                        )
                else:
                    event_end_local = None

                formatted_date = event_start_local.strftime("%d %B, %A")
                date_parts = formatted_date.split(" ")

                forecast_date_key = event_start_local.strftime("%Y-%m-%d")

                is_all_day = event_start_local.time() == time.min and (
                    not event_end_local or event_end_local.time() == time.min
                )

                start_time_12hr = (
                    event_start_local.strftime("%I:%M %p") if not is_all_day else None
                )
                end_time_12hr = (
                    event_end_local.strftime("%I:%M %p")
                    if event_end_local and not is_all_day
                    else None
                )

                forecast_data = forecast.get(forecast_date_key, {}) if forecast else {}
                if forecast_data:
                    forecast_data["maxtemp_f"] = safe_round(
                        forecast_data.get("maxtemp_f")
                    )
                    forecast_data["mintemp_f"] = safe_round(
                        forecast_data.get("mintemp_f")
                    )

                event_dict = {
                    "summary": str(event.get("SUMMARY", "Unnamed Event")),
                    "description": str(event.get("DESCRIPTION", "")),
                    "location": str(event.get("LOCATION", "")),
                    "start_time": start_time_12hr,
                    "end_time": end_time_12hr,
                    "date": formatted_date,
                    "forecast_date_key": forecast_date_key,
                    "day": date_parts[0],
                    "month": date_parts[1].strip(","),
                    "weekday": date_parts[2],
                    "is_all_day": is_all_day,
                    "forecast_data": forecast_data,
                    "source": source,
                    "is_next_event": False,
                    "_start_datetime_obj": event_start_local,
                }

                all_events.append(event_dict)

        # Group events by date
        grouped_events = {}
        for e in all_events:
            formatted_date = e["date"]
            if formatted_date not in grouped_events:
                grouped_events[formatted_date] = []
            grouped_events[formatted_date].append(e)

        # Sort events within each date by time
        for date_key in grouped_events:
            grouped_events[date_key] = sorted(
                grouped_events[date_key],
                key=lambda e: (
                    e["_start_datetime_obj"].time() if not e["is_all_day"] else time.min
                ),
            )

        # Sort the grouped events by date (chronological order)
        grouped_events = dict(
            sorted(
                grouped_events.items(),
                key=lambda item: min(e["_start_datetime_obj"] for e in item[1]),
            )
        )

        # Determine the next event
        try:
            next_event_found = False  # Track if the next event has been marked
            for date_key, events in grouped_events.items():
                for event in events:
                    # Compare event's start datetime object with the current datetime
                    if event["_start_datetime_obj"] >= today:
                        if not next_event_found:
                            event["is_next_event"] = True
                            next_event_found = True
                        else:
                            event["is_next_event"] = False
                    else:
                        event["is_next_event"] = False

                # Stop checking once the next event is found
                if next_event_found:
                    break

            # Remove private `_start_datetime_obj` from output
            for date_key in grouped_events:
                grouped_events[date_key] = [
                    {k: v for k, v in e.items() if k != "_start_datetime_obj"}
                    for e in grouped_events[date_key]
                ]

        except Exception as e:
            logging.debug(f"Error determining the next event: {e}")

    except requests.exceptions.RequestException as e:
        logging.debug(f"Error fetching calendar data: {e}")

    except Exception as e:
        logging.debug(f"An unexpected error occurred: {e}")

    return grouped_events
