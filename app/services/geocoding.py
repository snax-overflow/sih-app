"""Geocoding and nearby-place lookup helpers."""

import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": "YatriSahayak/1.0"}
REQUEST_TIMEOUT_SECONDS = 15


class SearchService:
    @staticmethod
    def _nominatim(params):
        try:
            response = requests.get(
                NOMINATIM_URL, params=params, headers=HEADERS, timeout=REQUEST_TIMEOUT_SECONDS
            )
            response.raise_for_status()
            return response.json(), None
        except (requests.RequestException, ValueError):
            return None, "Unable to contact the location service. Please try again."

    @staticmethod
    def _overpass_nearby(lat: float, lon: float, radius_m: int = 10000, limit: int = 5):
        """Query Overpass API for tourism POIs within radius_m metres of lat/lon."""
        query = f"""
[out:json][timeout:10];
(
  node["tourism"](around:{radius_m},{lat},{lon});
  way["tourism"](around:{radius_m},{lat},{lon});
);
out center {limit * 3};
"""
        try:
            response = requests.post(
                OVERPASS_URL, data={"data": query}, headers=HEADERS, timeout=REQUEST_TIMEOUT_SECONDS
            )
            response.raise_for_status()
            data = response.json()
            places = []
            seen = set()
            for el in data.get("elements", []):
                tags = el.get("tags", {})
                name = tags.get("name") or tags.get("name:en")
                if not name or name in seen:
                    continue
                seen.add(name)
                # nodes have lat/lon directly; ways have a center object
                if el["type"] == "node":
                    elat, elon = el["lat"], el["lon"]
                else:
                    center = el.get("center", {})
                    elat, elon = center.get("lat"), center.get("lon")
                if elat is None or elon is None:
                    continue
                places.append({"name": name, "lat": float(elat), "lon": float(elon)})
                if len(places) >= limit:
                    break
            return places, None
        except (requests.RequestException, ValueError, KeyError):
            return None, "Overpass API error"

    @staticmethod
    def find_destination_and_nearby(query: str):
        if not query:
            return None, "Destination query is required"

        main_data, error = SearchService._nominatim({"q": query, "format": "json", "limit": 1})
        if error:
            return None, error
        if not main_data:
            return None, "Destination not found"

        destination = main_data[0]
        main_place = {
            "name": destination["display_name"].split(",")[0],
            "full_name": destination["display_name"],
            "lat": float(destination["lat"]),
            "lon": float(destination["lon"]),
        }

        lat, lon = main_place["lat"], main_place["lon"]

        # Try Overpass first (most reliable for tourism POIs)
        nearby_places, ov_error = SearchService._overpass_nearby(lat, lon, radius_m=10000, limit=5)

        # Fallback to Nominatim viewbox if Overpass fails
        if ov_error or not nearby_places:
            delta = 0.25
            fallback_data, _ = SearchService._nominatim({
                "q": query,
                "format": "json",
                "limit": 10,
                "viewbox": f"{lon - delta},{lat + delta},{lon + delta},{lat - delta}",
                "bounded": 1,
            })
            nearby_places = []
            for item in (fallback_data or []):
                item_name = item.get("display_name", "").split(",")[0]
                if item_name != main_place["name"]:
                    nearby_places.append({
                        "name": item_name,
                        "lat": float(item["lat"]),
                        "lon": float(item["lon"]),
                    })
                if len(nearby_places) >= 5:
                    break

        return {"main": main_place, "nearby": nearby_places}, None
