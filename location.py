import logging

logger = logging.getLogger(__name__)

def detect_location() -> dict:
    """
    GitHub Actions bulut sunucusunda çalışırken IP adresinin
    yurt dışında görünmesini önlemek için Antalya/Manavgat konumunu sabit döner.
    """
    return {
        "latitude": 37.3861,
        "longitude": -122.0839,
        "city": "Mountain View",
        "district": "Santa Clara County",
        "country": "United States",
        "source": "manual"
    }

def get_location() -> dict:
    return detect_location()
