"""
Geocoding and Nearby-Place Lookup Service.

This module handles interactions with external OpenStreetMap APIs:
1. Nominatim: Converts location names (e.g., "Mumbai") into coordinates (lat/lon).
2. Overpass API: Queries specific points of interest (POIs) based on coordinates.
"""

import requests

# API Endpoints and Configuration
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
# OpenStreetMap requires a custom User-Agent. 'YatriSahayak' is your app's identifier!
HEADERS = {"User-Agent": "YatriSahayak/1.0"}
REQUEST_TIMEOUT_SECONDS = 15


class SearchService:
    """
    Service class that isolates all external API logic for location fetching.
    Uses @staticmethod so we don't have to instantiate the class to use its functions.
    """

    @staticmethod
    def _nominatim(params):
        """
        Internal helper to make requests to the Nominatim Geocoding API.
        
        Args:
            params (dict): Query parameters to send in the URL.
            
        Returns:
            tuple: (JSON response data, Error message if any)
        """
        try:
            response = requests.get(
                NOMINATIM_URL, params=params, headers=HEADERS, timeout=REQUEST_TIMEOUT_SECONDS
            )
            response.raise_for_status() # Throws an error if we get a 4xx or 5xx HTTP response
            return response.json(), None
        except (requests.RequestException, ValueError):
            return None, "Unable to contact the location service. Please try again."

    @staticmethod
    def _overpass_nearby(lat: float, lon: float, radius_m: int = 10000, limit: int = 5):
        """
        Queries the Overpass API for tourism Points of Interest (POIs) around a specific coordinate.
        
        Args:
            lat (float): Latitude of the center point.
            lon (float): Longitude of the center point.
            radius_m (int): Search radius in meters (default 10km).
            limit (int): Max number of places to return.
            
        Returns:
            tuple: (List of place dictionaries, Error message if any)
        """
        # This is "Overpass QL" (Query Language). 
        # It looks for nodes (points) and ways (areas/buildings) tagged as "tourism".
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
            seen = set() # Used to prevent duplicate places with the same name
            
            for el in data.get("elements", []):
                tags = el.get("tags", {})
                name = tags.get("name") or tags.get("name:en")
                
                # Skip if there's no name, or if we've already added this place
                if not name or name in seen:
                    continue
                seen.add(name)
                
                # 'nodes' have direct lat/lon. 'ways' are shapes, so we grab their center point.
                if el["type"] == "node":
                    elat, elon = el["lat"], el["lon"]
                else:
                    center = el.get("center", {})
                    elat, elon = center.get("lat"), center.get("lon")
                    
                if elat is None or elon is None:
                    continue
                    
                # Format the valid place and add it to our list
                places.append({"name": name, "lat": float(elat), "lon": float(elon)})
                
                # Stop looking once we hit our limit
                if len(places) >= limit:
                    break
                    
            return places, None
            
        except (requests.RequestException, ValueError, KeyError):
            return None, "Overpass API error"

    @staticmethod
    def find_destination_and_nearby(query: str):
        """
        The main orchestrator function called by our Flask routes.
        It gets the main destination coordinates, then fetches nearby tourist spots.
        
        Args:
            query (str): The location the user searched for (e.g., "Paris").
            
        Returns:
            tuple: (Dictionary containing 'main' and 'nearby' places, Error message)
        """
        if not query:
            return None, "Destination query is required"

        # 1. Ask Nominatim to turn the user's text query into coordinates
        main_data, error = SearchService._nominatim({"q": query, "format": "json", "limit": 1})
        if error:
            return None, error
        if not main_data:
            return None, "Destination not found"

        # 2. Extract the best match
        destination = main_data[0]
        main_place = {
            "name": destination["display_name"].split(",")[0], # Get just the first part (e.g., "Paris")
            "full_name": destination["display_name"],          # Keep the full string for details
            "lat": float(destination["lat"]),
            "lon": float(destination["lon"]),
        }

        lat, lon = main_place["lat"], main_place["lon"]

        # 3. Try to get tourism spots nearby using Overpass
        nearby_places, ov_error = SearchService._overpass_nearby(lat, lon, radius_m=10000, limit=5)

        # 4. FALLBACK LOGIC: If Overpass is down or empty, use Nominatim again
        if ov_error or not nearby_places:
            delta = 0.25 # Creates a "viewbox" (bounding box) around the original coordinates
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
                # Make sure we don't list the main destination as a "nearby" place
                if item_name != main_place["name"]:
                    nearby_places.append({
                        "name": item_name,
                        "lat": float(item["lat"]),
                        "lon": float(item["lon"]),
                    })
                if len(nearby_places) >= 5:
                    break

        # 5. Return the final beautifully packaged data
        return {"main": main_place, "nearby": nearby_places}, None