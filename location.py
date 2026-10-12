import logging

logger = logging.getLogger(__name__)

def detect_location() -> dict:
    """
    GitHub Actions bulut sunucusunda çalışırken IP adresinin
    yurt dışında görünmesini önlemek için Antalya/Manavgat konumunu sabit döner.
    """
    return {
        "latitude": 41.1995,
        "longitude": 29.0485,
        "city": "İstanbul",
        "district": "Sarıyer",
        "country": "Türkiye",
        "source": "manual"
    }

def get_location() -> dict:
    return detect_location()
