import os
import requests
from langchain_core.tools import tool

OPENTRIPMAP_API_KEY = os.getenv("OPENTRIPMAP_API_KEY")

@tool
def get_attractions(city_name: str) -> str:
    """Returns a list of notable attractions in a given city."""
    if not OPENTRIPMAP_API_KEY:
        return "[TOOL ERROR] Missing OpenTripMap API key."

    try:
        coord_url = "https://api.opentripmap.com/0.1/en/places/geoname"
        coord_res = requests.get(coord_url, params={
            "name": city_name,
            "apikey": OPENTRIPMAP_API_KEY
        })
        coord_res.raise_for_status()
        geo = coord_res.json()
        lon, lat = geo["lon"], geo["lat"]

        places_url = "https://api.opentripmap.com/0.1/en/places/radius"
        places_res = requests.get(places_url, params={
            "lon": lon,
            "lat": lat,
            "radius": 5000,
            "limit": 20,
            "rate": 2,
            "format": "json",
            "apikey": OPENTRIPMAP_API_KEY
        })
        places_res.raise_for_status()
        places = places_res.json()

        if not places:
            return f"No notable attractions found in {city_name}."

        result = f"Top attractions in {city_name}:\n"
        for place in places:
            name = place.get("name", "Unnamed location")
            kind = place.get("kinds", "").split(",")[0]
            result += f"- {name} ({kind})\n"

        return result.strip()

    except Exception as e:
        return f"[TOOL ERROR] Failed to fetch attractions for {city_name}: {str(e)}"