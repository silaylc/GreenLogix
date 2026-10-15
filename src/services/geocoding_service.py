import requests

def geocode_address(address: str):
    """Adresi koordinata çevirir."""
    if not address:
        return None
    
    url = "https://nominatim.openstreetmap.org/search"
    headers = {"User-Agent": "GreenLogix_App_v2"}
    params = {
        "q": address,
        "format": "json",
        "limit": 1,
        "countrycodes": "tr"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        data = response.json()
        if data:
            return {
                "lat": float(data[0]["lat"]),
                "lon": float(data[0]["lon"]),
                "label": data[0]["display_name"]
            }
    except Exception:
        return None
    return None