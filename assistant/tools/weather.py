import os
import requests
from collections import defaultdict
from datetime import datetime
from langchain_core.tools import tool

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
BASE_CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
BASE_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

def _fetch_weather_data(url: str, city_name: str) -> dict | str:
    if not WEATHER_API_KEY:
        return "[TOOL ERROR] Missing or invalid WEATHER_API_KEY"

    params = {
        "q": city_name,
        "appid": WEATHER_API_KEY,
        "units": "metric"
    }

    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        data = res.json()
        return data

    except requests.exceptions.HTTPError:
        if res.status_code == 404:
            return f"[TOOL ERROR] City '{city_name}' not found. Please check the spelling."
        return f"[TOOL ERROR] Weather service returned status code {res.status_code}."
    except Exception as e:
        return f"[TOOL ERROR] Unexpected error: {str(e)}"


@tool
def get_weather_current(city_name: str) -> str:
    """Given a city name returns the current weather for the city."""
    data = _fetch_weather_data(BASE_CURRENT_URL, city_name)
    if isinstance(data, str):
        return data  # Error message

    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"]
    location = f'{data.get("name", city_name)}, {data["sys"].get("country", "")}'

    return f"Current weather in {location}: {desc}, {temp:.1f}°C."


@tool
def get_weather_forecast(city_name: str) -> str:
    """Returns a 5-day weather forecast for a given city."""
    data = _fetch_weather_data(BASE_FORECAST_URL, city_name)
    if isinstance(data, str):
        return data  # Error message

    forecasts = data.get("list")
    if not forecasts:
        return f"No forecast data available for {city_name}."

    daily_data = defaultdict(list)

    for item in forecasts:
        date = item["dt_txt"].split(" ")[0]
        temp_min = item["main"]["temp_min"]
        temp_max = item["main"]["temp_max"]
        desc = item["weather"][0]["description"]
        daily_data[date].append((temp_min, temp_max, desc))

    today = datetime.now().strftime('%Y-%m-%d')
    lines = []

    for date, entries in sorted(daily_data.items()):
        if date == today:
            continue

        temps_min = [e[0] for e in entries]
        temps_max = [e[1] for e in entries]
        descriptions = [e[2] for e in entries]
        most_common_desc = max(set(descriptions), key=descriptions.count)
        label = datetime.strptime(date, "%Y-%m-%d").strftime("%A")

        lines.append(f"{label}: {most_common_desc}, {min(temps_min):.1f}°C – {max(temps_max):.1f}°C")

    return f"5-day forecast for {city_name}:\n" + "\n".join(lines)