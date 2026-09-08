import logging

logger = logging.getLogger(__name__)

def detect_location() -> dict:
    """
    GitHub Actions bulut sunucusunda çalışırken IP adresinin
    yurt dışında görünmesini önlemek için Antalya/Manavgat konumunu sabit döner.
    """
    return {
        "latitude": 36.786869,
        "longitude": 31.441282,
        "city": "Antalya",
        "district": "Manavgat",
        "country": "Türkiye",
        "source": "manual"
    }

def get_location() -> dict:
    return detect_location()
