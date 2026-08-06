"""
weather.py — Open-Meteo API'den saatlik hava durumu verisi çekme modülü.

Open-Meteo, birden fazla ulusal meteoroloji ajansından (ECMWF, NOAA, DWD)
veri toplayan ücretsiz ve açık kaynaklı bir hava durumu API'sidir.
API anahtarı gerektirmez.
"""

import requests
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

# Open-Meteo API endpoint'i
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def get_hourly_forecast(latitude: float, longitude: float) -> list[dict]:
    """
    Belirtilen koordinatlar için bugünün saatlik hava durumu tahminini çeker.

    Args:
        latitude: Enlem değeri (örn: 41.0082 for İstanbul)
        longitude: Boylam değeri (örn: 28.9784 for İstanbul)

    Returns:
        Saatlik verileri içeren sözlük listesi. Her eleman:
        {
            "hour": "08:00",
            "temperature": 25.3,
            "precipitation_probability": 10
        }

    Raises:
        requests.RequestException: API isteği başarısız olursa
        ValueError: API yanıtı beklenmeyen formatta ise
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,precipitation_probability",
        "timezone": "auto",  # Koordinatlara göre otomatik saat dilimi
        "forecast_days": 1    # Sadece bugünün verisini çek
    }

    logger.info(f"Open-Meteo API'ye istek gönderiliyor: lat={latitude}, lon={longitude}")

    try:
        response = requests.get(OPEN_METEO_URL, params=params, timeout=15)
        response.raise_for_status()
    except requests.ConnectionError:
        logger.error("İnternet bağlantısı kurulamadı.")
        raise
    except requests.Timeout:
        logger.error("API isteği zaman aşımına uğradı (15s).")
        raise
    except requests.HTTPError as e:
        logger.error(f"API HTTP hatası: {e.response.status_code}")
        raise

    data = response.json()

    # API yanıtını doğrula
    if "hourly" not in data:
        raise ValueError("API yanıtında 'hourly' verisi bulunamadı.")

    hourly = data["hourly"]
    required_keys = ["time", "temperature_2m", "precipitation_probability"]
    for key in required_keys:
        if key not in hourly:
            raise ValueError(f"API yanıtında '{key}' alanı eksik.")

    # Bugünün tarihini al ve sadece bugünün verilerini filtrele
    today_str = date.today().isoformat()

    result = []
    for i, time_str in enumerate(hourly["time"]):
        # Open-Meteo zaman formatı: "2026-07-28T08:00"
        if not time_str.startswith(today_str):
            continue

        dt = datetime.fromisoformat(time_str)
        result.append({
            "hour": dt.strftime("%H:%M"),
            "temperature": hourly["temperature_2m"][i],
            "precipitation_probability": hourly["precipitation_probability"][i]
        })

    logger.info(f"Toplam {len(result)} saatlik veri alındı.")
    return result
