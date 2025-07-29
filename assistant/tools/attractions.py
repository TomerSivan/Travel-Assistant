import os
import requests
from langchain_core.tools import tool

# Get OpenTripMap API key from environment variables
OPENTRIPMAP_API_KEY = os.getenv("OPENTRIPMAP_API_KEY")

@tool
def get_attractions(city_name: str) -> str:
    """
    Tool: Fetches a list of notable attractions for a given city.

    This tool first resolves the latitude and longitude of the city using the
    OpenTripMap Geoname API. Then, it queries nearby points of interest (POIs)
    using the Radius API, filtering by popularity. For a readable summary.

    :param city_name: Name of the city to search attractions for
    :return: List of readable attractions or a error message
    """
    if not OPENTRIPMAP_API_KEY:
        return "[TOOL ERROR] Missing OpenTripMap API key."

    try:
        # Get geographic coordinates of the city
        coord_url = "https://api.opentripmap.com/0.1/en/places/geoname"
        coord_res = requests.get(coord_url, params={
            "name": city_name,
            "apikey": OPENTRIPMAP_API_KEY
        })
        coord_res.raise_for_status()
        geo = coord_res.json()
        lon, lat = geo["lon"], geo["lat"]

        # Search for nearby attractions using radius-based query
        places_url = "https://api.opentripmap.com/0.1/en/places/radius"
        places_res = requests.get(places_url, params={
            "lon": lon,
            "lat": lat,
            "radius": 5000,    # Search within 5km
            "limit": 20,       # Limit results to top 20
            "rate": 2,         # Only include highly rated places
            "format": "json",
            "apikey": OPENTRIPMAP_API_KEY
        })
        places_res.raise_for_status()
        places = places_res.json()

        if not places:
            return f"No notable attractions found in {city_name}."

        # Format and return results
        result = f"Top attractions in {city_name}:\n"
        for place in places:
            name = place.get("name", "Unnamed location")
            kind = place.get("kinds", "").split(",")[0]
            result += f"- {name} ({kind})\n"

        return result.strip()

    except Exception as e:
        return f"[TOOL ERROR] Failed to fetch attractions for {city_name}: {str(e)}"