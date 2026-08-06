"""
location.py — IP tabanlı otomatik konum tespit modülü.

Kullanıcının mevcut IP adresine göre konum bilgisini (enlem, boylam, şehir)
otomatik olarak tespit eder. Ücretsiz ip-api.com servisini kullanır.

Eğer .env dosyasında LATITUDE ve LONGITUDE tanımlıysa onları kullanır,
tanımlı değilse otomatik konum tespiti yapar.
"""

import os
import requests
import logging

logger = logging.getLogger(__name__)

# Ücretsiz IP tabanlı konum servisi (API anahtarı gerektirmez)
IP_API_URL = "http://ip-api.com/json/"


def detect_location() -> dict:
    """
    IP adresine göre mevcut konumu otomatik tespit eder.

    Returns:
        {
            "latitude": 41.0082,
            "longitude": 28.9784,
            "city": "İstanbul",
            "country": "Turkey",
            "source": "auto"  # veya "manual"
        }

    Raises:
        RuntimeError: Konum tespit edilemezse
    """
    # Önce .env'de manuel koordinat var mı kontrol et
    env_lat = os.getenv("LATITUDE", "").strip()
    env_lon = os.getenv("LONGITUDE", "").strip()

    if env_lat and env_lon:
        try:
            lat = float(env_lat)
            lon = float(env_lon)
            logger.info(f"Manuel konum kullanılıyor: lat={lat}, lon={lon}")
            return {
                "latitude": lat,
                "longitude": lon,
                "city": "Manuel konum",
                "country": "",
                "source": "manual"
            }
        except ValueError:
            logger.warning("LATITUDE/LONGITUDE değerleri geçersiz, otomatik konum tespitine geçiliyor.")

    # Otomatik IP tabanlı konum tespiti
    logger.info("Otomatik konum tespiti yapılıyor (IP tabanlı)...")

    try:
        response = requests.get(IP_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Konum servisi yanıt vermedi: {e}")

    if data.get("status") != "success":
        raise RuntimeError(f"Konum tespit edilemedi: {data.get('message', 'Bilinmeyen hata')}")

    result = {
        "latitude": data["lat"],
        "longitude": data["lon"],
        "city": data.get("city", "Bilinmeyen"),
        "country": data.get("country", ""),
        "source": "auto"
    }

    logger.info(
        f"Konum tespit edildi: {result['city']}, {result['country']} "
        f"(lat={result['latitude']}, lon={result['longitude']})"
    )
    return result
