"""
Geocoding utilities using OpenStreetMap Nominatim (free, no API key).
Rate limit: 1 request/second — fine for property saves.
"""
import math
import time
import urllib.request
import urllib.parse
import json
import logging

logger = logging.getLogger(__name__)

# Nominatim endpoint
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
# User-Agent is required by Nominatim usage policy
USER_AGENT = "RentSathiNepal/1.0 (info@rentsathi.com.np)"


def geocode_address(address: str, city: str = "", country: str = "Nepal") -> tuple[float, float] | None:
    """
    Convert an address string to (latitude, longitude) using Nominatim.
    Returns None if geocoding fails.
    
    Usage policy: max 1 request/second, must include User-Agent.
    """
    # Build a search query — more specific = more accurate
    parts = [p for p in [address, city, country] if p.strip()]
    query = ", ".join(parts)

    params = urllib.parse.urlencode({
        "q": query,
        "format": "json",
        "limit": 1,
        "countrycodes": "np",   # restrict to Nepal
    })

    url = f"{NOMINATIM_URL}?{params}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            if data:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                return lat, lon
    except Exception as e:
        logger.warning(f"Geocoding failed for '{query}': {e}")

    # Fallback: try with just city + country
    if city:
        params2 = urllib.parse.urlencode({
            "q": f"{city}, Nepal",
            "format": "json",
            "limit": 1,
            "countrycodes": "np",
        })
        try:
            req2 = urllib.request.Request(
                f"{NOMINATIM_URL}?{params2}",
                headers={"User-Agent": USER_AGENT}
            )
            with urllib.request.urlopen(req2, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                if data:
                    return float(data[0]["lat"]), float(data[0]["lon"])
        except Exception as e:
            logger.warning(f"Geocoding city fallback failed for '{city}': {e}")

    return None


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Haversine formula — great-circle distance between two points in km.
    """
    R = 6371.0  # Earth radius in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def format_distance(km: float) -> str:
    """Human-readable distance string."""
    if km < 1.0:
        return f"{int(km * 1000)} m away"
    return f"{km:.1f} km away"
