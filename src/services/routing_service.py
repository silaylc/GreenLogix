import requests

def get_route_for_points(coordinates: list):
    """
    OSRM API kullanarak koordinatlar arası gerçek yol verisini çeker.
    Girdi formatı: [(lon1, lat1), (lon2, lat2), ...]
    """
    if not coordinates or len(coordinates) < 2:
        return None

    # Koordinatları string formatına getir (lon,lat;lon,lat)
    coords_str = ";".join([f"{lon},{lat}" for lon, lat in coordinates])
    url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}"
    
    params = {
        "overview": "full",
        "geometries": "geojson"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("code") == "Ok":
            route = data["routes"][0]
            return {
                "distance_m": route["distance"],
                "duration_s": route["duration"],
                "geometry": route["geometry"] # Harita çizimi için gerekli
            }
    except Exception as e:
        print(f"Routing Error: {e}")
        return None
    return None