import json
import os

import requests
from datetime import datetime
from dotenv import load_dotenv


from scripts.hfe_logging import configure_logging

logging = configure_logging()
load_dotenv()

"""
https://www.weatherapi.com/docs/#apis-forecast

to look at:
https://freesvgicons.com/search?q=weather

"""


def fontawesome_icon(code: int = 1000, day: int = 1):
    """
    docs : https://fontawesome.com/icons/categories/weather
    :param code: Weather code integer
    :param day: Weather code integer
    :return: Dictionary containing weather details including 'fa_icon' and 'fa_icon_night'
    """
    weather_dict = {
        1000: {
            "day": "Sunny",
            "night": "Clear",
            "icon": 113,
            "fa_icon_day": "fa-sun",
            "fa_icon_night": "fa-moon",
        },
        1003: {
            "day": "Partly cloudy",
            "night": "Partly cloudy",
            "icon": 116,
            "fa_icon_day": "fa-cloud-sun",
            "fa_icon_night": "fa-cloud-moon",
        },
        1006: {
            "day": "Cloudy",
            "night": "Cloudy",
            "icon": 119,
            "fa_icon_day": "fa-cloud",
            "fa_icon_night": "fa-cloud",
        },
        1009: {
            "day": "Overcast",
            "night": "Overcast",
            "icon": 122,
            "fa_icon_day": "fa-cloud",
            "fa_icon_night": "fa-cloud",
        },
        1030: {
            "day": "Mist",
            "night": "Mist",
            "icon": 143,
            "fa_icon_day": "fa-smog",
            "fa_icon_night": "fa-smog",
        },
        1063: {
            "day": "Patchy rain possible",
            "night": "Patchy rain possible",
            "icon": 176,
            "fa_icon_day": "fa-cloud-rain",
            "fa_icon_night": "fa-cloud-rain",
        },
        1066: {
            "day": "Patchy snow possible",
            "night": "Patchy snow possible",
            "icon": 179,
            "fa_icon_day": "fa-snowflake",
            "fa_icon_night": "fa-snowflake",
        },
        1069: {
            "day": "Patchy sleet possible",
            "night": "Patchy sleet possible",
            "icon": 182,
            "fa_icon_day": "fa-cloud-sleet",
            "fa_icon_night": "fa-cloud-sleet",
        },
        1072: {
            "day": "Patchy freezing drizzle possible",
            "night": "Patchy freezing drizzle possible",
            "icon": 185,
            "fa_icon_day": "fa-cloud-rain",
            "fa_icon_night": "fa-cloud-rain",
        },
        1087: {
            "day": "Thundery outbreaks possible",
            "night": "Thundery outbreaks possible",
            "icon": 200,
            "fa_icon_day": "fa-bolt",
            "fa_icon_night": "fa-bolt",
        },
        1114: {
            "day": "Blowing snow",
            "night": "Blowing snow",
            "icon": 227,
            "fa_icon_day": "fa-snowflake",
            "fa_icon_night": "fa-snowflake",
        },
        1117: {
            "day": "Blizzard",
            "night": "Blizzard",
            "icon": 230,
            "fa_icon_day": "fa-snowflake",
            "fa_icon_night": "fa-snowflake",
        },
        1135: {
            "day": "Fog",
            "night": "Fog",
            "icon": 248,
            "fa_icon_day": "fa-smog",
            "fa_icon_night": "fa-smog",
        },
        1147: {
            "day": "Freezing fog",
            "night": "Freezing fog",
            "icon": 260,
            "fa_icon_day": "fa-smog",
            "fa_icon_night": "fa-smog",
        },
        1150: {
            "day": "Patchy light drizzle",
            "night": "Patchy light drizzle",
            "icon": 263,
            "fa_icon_day": "fa-cloud-rain",
            "fa_icon_night": "fa-cloud-rain",
        },
        1153: {
            "day": "Light drizzle",
            "night": "Light drizzle",
            "icon": 266,
            "fa_icon_day": "fa-cloud-rain",
            "fa_icon_night": "fa-cloud-rain",
        },
        1168: {
            "day": "Freezing drizzle",
            "night": "Freezing drizzle",
            "icon": 281,
            "fa_icon_day": "fa-cloud-rain",
            "fa_icon_night": "fa-cloud-rain",
        },
        1171: {
            "day": "Heavy freezing drizzle",
            "night": "Heavy freezing drizzle",
            "icon": 284,
            "fa_icon_day": "fa-cloud-showers-heavy",
            "fa_icon_night": "fa-cloud-showers-heavy",
        },
        1180: {
            "day": "Patchy light rain",
            "night": "Patchy light rain",
            "icon": 293,
            "fa_icon_day": "fa-cloud-rain",
            "fa_icon_night": "fa-cloud-rain",
        },
        1183: {
            "day": "Light rain",
            "night": "Light rain",
            "icon": 296,
            "fa_icon_day": "fa-cloud-rain",
            "fa_icon_night": "fa-cloud-rain",
        },
        1186: {
            "day": "Moderate rain at times",
            "night": "Moderate rain at times",
            "icon": 299,
            "fa_icon_day": "fa-cloud-showers-heavy",
            "fa_icon_night": "fa-cloud-showers-heavy",
        },
        1189: {
            "day": "Moderate rain",
            "night": "Moderate rain",
            "icon": 302,
            "fa_icon_day": "fa-cloud-showers-heavy",
            "fa_icon_night": "fa-cloud-showers-heavy",
        },
        1192: {
            "day": "Heavy rain at times",
            "night": "Heavy rain at times",
            "icon": 305,
            "fa_icon_day": "fa-cloud-showers-heavy",
            "fa_icon_night": "fa-cloud-showers-heavy",
        },
        1195: {
            "day": "Heavy rain",
            "night": "Heavy rain",
            "icon": 308,
            "fa_icon_day": "fa-cloud-showers-heavy",
            "fa_icon_night": "fa-cloud-showers-heavy",
        },
        1198: {
            "day": "Light freezing rain",
            "night": "Light freezing rain",
            "icon": 311,
            "fa_icon_day": "fa-cloud-rain",
            "fa_icon_night": "fa-cloud-rain",
        },
        1201: {
            "day": "Moderate or heavy freezing rain",
            "night": "Moderate or heavy freezing rain",
            "icon": 314,
            "fa_icon_day": "fa-cloud-showers-heavy",
            "fa_icon_night": "fa-cloud-showers-heavy",
        },
        1204: {
            "day": "Light sleet",
            "night": "Light sleet",
            "icon": 317,
            "fa_icon_day": "fa-cloud-sleet",
            "fa_icon_night": "fa-cloud-sleet",
        },
        1207: {
            "day": "Moderate or heavy sleet",
            "night": "Moderate or heavy sleet",
            "icon": 320,
            "fa_icon_day": "fa-cloud-sleet",
            "fa_icon_night": "fa-cloud-sleet",
        },
        1210: {
            "day": "Patchy light snow",
            "night": "Patchy light snow",
            "icon": 323,
            "fa_icon_day": "fa-snowflake",
            "fa_icon_night": "fa-snowflake",
        },
        1213: {
            "day": "Light snow",
            "night": "Light snow",
            "icon": 326,
            "fa_icon_day": "fa-snowflake",
            "fa_icon_night": "fa-snowflake",
        },
        1216: {
            "day": "Patchy moderate snow",
            "night": "Patchy moderate snow",
            "icon": 329,
            "fa_icon_day": "fa-snowflake",
            "fa_icon_night": "fa-snowflake",
        },
        1219: {
            "day": "Moderate snow",
            "night": "Moderate snow",
            "icon": 332,
            "fa_icon_day": "fa-snowflake",
            "fa_icon_night": "fa-snowflake",
        },
        1222: {
            "day": "Patchy heavy snow",
            "night": "Patchy heavy snow",
            "icon": 335,
            "fa_icon_day": "fa-snowflake",
            "fa_icon_night": "fa-snowflake",
        },
        1225: {
            "day": "Heavy snow",
            "night": "Heavy snow",
            "icon": 338,
            "fa_icon_day": "fa-snowflake",
            "fa_icon_night": "fa-snowflake",
        },
        1237: {
            "day": "Ice pellets",
            "night": "Ice pellets",
            "icon": 350,
            "fa_icon_day": "fa-cloud-hail",
            "fa_icon_night": "fa-cloud-hail",
        },
        1240: {
            "day": "Light rain shower",
            "night": "Light rain shower",
            "icon": 353,
            "fa_icon_day": "fa-cloud-rain",
            "fa_icon_night": "fa-cloud-rain",
            "fa_icon_night": "fa-cloud-rain",
        },
        1243: {
            "day": "Moderate or heavy rain shower",
            "night": "Moderate or heavy rain shower",
            "icon": 356,
            "fa_icon_day": "fa-cloud-showers-heavy",
            "fa_icon_night": "fa-cloud-showers-heavy",
        },
        1246: {
            "day": "Torrential rain shower",
            "night": "Torrential rain shower",
            "icon": 359,
            "fa_icon_day": "fa-cloud-showers-heavy",
            "fa_icon_night": "fa-cloud-showers-heavy",
        },
        1249: {
            "day": "Light sleet showers",
            "night": "Light sleet showers",
            "icon": 362,
            "fa_icon_day": "fa-cloud-sleet",
            "fa_icon_night": "fa-cloud-sleet",
        },
        1252: {
            "day": "Moderate or heavy sleet showers",
            "night": "Moderate or heavy sleet showers",
            "icon": 365,
            "fa_icon_day": "fa-cloud-sleet",
            "fa_icon_night": "fa-cloud-sleet",
        },
        1255: {
            "day": "Light snow showers",
            "night": "Light snow showers",
            "icon": 368,
            "fa_icon_day": "fa-snowflake",
            "fa_icon_night": "fa-snowflake",
        },
        1258: {
            "day": "Moderate or heavy snow showers",
            "night": "Moderate or heavy snow showers",
            "icon": 371,
            "fa_icon_day": "fa-snowflake",
            "fa_icon_night": "fa-snowflake",
        },
        1261: {
            "day": "Light showers of ice pellets",
            "night": "Light showers of ice pellets",
            "icon": 374,
            "fa_icon_day": "fa-cloud-hail",
            "fa_icon_night": "fa-cloud-hail",
        },
        1264: {
            "day": "Moderate or heavy showers of ice pellets",
            "night": "Moderate or heavy showers of ice pellets",
            "icon": 377,
            "fa_icon_day": "fa-cloud-hail",
            "fa_icon_night": "fa-cloud-hail",
        },
        1273: {
            "day": "Patchy light rain with thunder",
            "night": "Patchy light rain with thunder",
            "icon": 386,
            "fa_icon_day": "fa-cloud-bolt-sun",
            "fa_icon_night": "fa-cloud-bolt-moon",
        },
        1276: {
            "day": "Moderate or heavy rain with thunder",
            "night": "Moderate or heavy rain with thunder",
            "icon": 389,
            "fa_icon_day": "fa-cloud-bolt-sun",
            "fa_icon_night": "fa-cloud-bolt-moon",
        },
        1279: {
            "day": "Patchy light snow with thunder",
            "night": "Patchy light snow with thunder",
            "icon": 392,
            "fa_icon_day": "fa-bolt",  # fix
            "fa_icon_day": "fa-bolt",  # fix
        },
        1282: {
            "day": "Moderate or heavy snow with thunder",
            "night": "Moderate or heavy snow with thunder",
            "icon": 395,
            "fa_icon_day": "fa-bolt",  # fix
            "fa_icon_day": "fa-bolt",  # fix
        },
    }

    data = weather_dict.get(
        code,
        {
            "day": "Unknown",
            "night": "Unknown",
            "icon": None,
            "fa_icon_day": "fa-question-circle",
            "fa_icon_night": "fa-question-circle",
        },
    )

    if not day:
        return data["fa_icon_night"]
    return data["fa_icon_day"]


def get_forecast_cached_data(zipcode="34688", forecast_file="forecast"):
    cache_files = {
        "forecast": f"{zipcode}_forecast_cache.json",
        "current": f"{zipcode}_current_data_cache.json",
        "astro": f"{zipcode}_astro_cache.json",
    }

    file_to_open = cache_files.get(forecast_file, cache_files["forecast"])

    if os.path.exists(file_to_open):
        with open(file_to_open, "r") as file:
            cached_data = json.load(file)
        return cached_data["data"]
    else:
        return {}


def get_forecast_data_or_cached(
    zipcode="34688", days=3, cache_duration=900, file_type="forecast"
):
    rapidapi_key = os.getenv("weatherapi_key", "")
    headers = {
        "x-rapidapi-host": "weatherapi-com.p.rapidapi.com",
        "x-rapidapi-key": rapidapi_key,
    }
    querystring = {"q": zipcode, "days": days}
    api_url = "https://weatherapi-com.p.rapidapi.com/forecast.json"

    cache_files = {
        "forecast": f"{zipcode}_forecast_cache.json",
        "current": f"{zipcode}_current_data_cache.json",
        "astro": f"{zipcode}_astro_cache.json",
    }

    file_to_open = cache_files.get(file_type, cache_files["current"])

    # Check if cache exists and is valid
    if os.path.exists(file_to_open):
        with open(file_to_open, "r") as file:
            cached_data = json.load(file)
        cached_time = datetime.fromisoformat(cached_data["timestamp"])
        if (datetime.now() - cached_time).total_seconds() < cache_duration:
            print("Returning cached weather data.")
            return cached_data["data"]

    # Fetch new data if cache is expired or missing
    try:
        response = requests.get(api_url, headers=headers, params=querystring)
        response.raise_for_status()
        weather_data = response.json()

        # Update all caches
        current_data = weather_data["current"]
        astro = weather_data["forecast"]["forecastday"][0]["astro"]
        current_data["condition"]["fa_icon"] = fontawesome_icon(
            code=weather_data["current"]["condition"]["code"],
            day=weather_data["current"]["is_day"],
        )

        forecast_list = {
            forecast_day["date"]: {
                "avghumidity": forecast_day["day"]["avghumidity"],
                "avgtemp_f": forecast_day["day"]["avgtemp_f"],
                "code": forecast_day["day"]["condition"]["code"],
                "daily_chance_of_rain": forecast_day["day"]["daily_chance_of_rain"],
                "daily_will_it_rain": forecast_day["day"]["daily_will_it_rain"],
                "maxtemp_f": forecast_day["day"]["maxtemp_f"],
                "maxwind_mph": forecast_day["day"]["maxwind_mph"],
                "mintemp_f": forecast_day["day"]["mintemp_f"],
                "totalprecip_in": forecast_day["day"]["totalprecip_in"],
                "uv": forecast_day["day"]["uv"],
                "is_sun_up": forecast_day["astro"]["is_sun_up"],
                "is_sun_up": forecast_day["astro"]["is_moon_up"],
                "fa_icon": fontawesome_icon(
                    code=forecast_day["day"]["condition"]["code"], day=1
                ),
            }
            for forecast_day in weather_data["forecast"]["forecastday"]
        }

        # Save updated cache
        for cache_name, data in [
            ("current", current_data),
            ("astro", astro),
            ("forecast", forecast_list),
        ]:
            with open(cache_files[cache_name], "w") as file:
                json.dump({"timestamp": datetime.now().isoformat(), "data": data}, file)

        return {"forecast": forecast_list, "current": current_data, "astro": astro}[
            file_type
        ]

    except requests.RequestException as e:
        logging.debug(f"Weather failed to fetch new weather data: {e}")
        if os.path.exists(file_to_open):
            with open(file_to_open, "r") as file:
                cached_data = json.load(file)
            logging.debug("Returning cached weather data due to API fetch failure.")
            return cached_data["data"]
        else:
            logging.debug("No weather cached data available.")
            return {}
