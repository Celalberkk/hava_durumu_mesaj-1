"""
main.py — Hava Durumu Uyarı Otomasyon Betiği (Ana Orkestrasyon)

Her sabah 08:30'da çalışarak:
1. Open-Meteo API'den saatlik hava durumu verisini çeker
2. Yağmur, yüksek sıcaklık ve düşük sıcaklık koşullarını kontrol eder
3. Uyarı mesajı oluşturur
4. Twilio WhatsApp üzerinden mesajı gönderir

Kullanım:
    Zamanlayıcı ile:  python main.py
    Anlık test:       python main.py --now
"""

import argparse
import logging
import sys
import os
import time

import schedule
from dotenv import load_dotenv

from weather import get_hourly_forecast
from alerts import check_rain_risk, check_high_temp, check_low_temp, build_alert_message
from notifier import send_whatsapp_message
from location import detect_location

# .env dosyasından konfigürasyonu yükle
load_dotenv()

# ─── Logging Yapılandırması ─────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("weather_alert.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)


def load_config() -> dict:
    """
    .env dosyasından gerekli konfigürasyon değerlerini yükler ve doğrular.

    Returns:
        Konfigürasyon sözlüğü

    Raises:
        SystemExit: Zorunlu bir değer eksikse
    """
    config = {
        "twilio_account_sid": os.getenv("TWILIO_ACCOUNT_SID"),
        "twilio_auth_token": os.getenv("TWILIO_AUTH_TOKEN"),
        "twilio_from_number": os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886"),
        "twilio_to_number": os.getenv("TWILIO_WHATSAPP_TO"),
    }

    # Zorunlu alanları kontrol et
    required = {
        "twilio_account_sid": "TWILIO_ACCOUNT_SID",
        "twilio_auth_token": "TWILIO_AUTH_TOKEN",
        "twilio_to_number": "TWILIO_WHATSAPP_TO",
    }

    missing = [env_name for key, env_name in required.items() if not config[key]]
    if missing:
        logger.error(
            f"Eksik konfigürasyon değerleri: {', '.join(missing)}. "
            f"Lütfen .env dosyasını kontrol edin."
        )
        sys.exit(1)

    return config


def run_weather_check():
    """
    Ana iş akışını çalıştırır:
    1. Hava durumu verisini çek
    2. Koşulları kontrol et
    3. Uyarı mesajı oluştur
    4. WhatsApp ile gönder
    """
    logger.info("=" * 60)
    logger.info("Hava durumu kontrolü başlatılıyor...")

    config = load_config()

    # ─── 1. Konumu tespit et ────────────────────────────────────────────────
    try:
        location = detect_location()
        city = location["city"]
        lat = location["latitude"]
        lon = location["longitude"]
        source_label = "otomatik (IP)" if location["source"] == "auto" else "manuel (.env)"
        logger.info(f"📍 Konum: {city} ({source_label})")
    except Exception as e:
        logger.error(f"Konum tespit edilemedi: {e}")
        return

    # ─── 2. Hava durumu verisini çek ───────────────────────────────────────
    try:
        hourly_data = get_hourly_forecast(lat, lon)
    except Exception as e:
        logger.error(f"Hava durumu verisi alınamadı: {e}")
        return

    if not hourly_data:
        logger.warning("Saatlik veri boş döndü, işlem sonlandırılıyor.")
        return

    # ─── 3. Koşulları kontrol et ──────────────────────────────────────────
    rain_hours = check_rain_risk(hourly_data)
    hot_hours = check_high_temp(hourly_data)
    cold_hours = check_low_temp(hourly_data)

    # ─── 4. Uyarı mesajı oluştur ─────────────────────────────────────────
    message = build_alert_message(rain_hours, hot_hours, cold_hours, city=city, hourly_data=hourly_data)
    logger.info(f"Oluşturulan mesaj:\n{message}")

    # ─── 5. WhatsApp ile gönder ──────────────────────────────────────────
    success = send_whatsapp_message(
        account_sid=config["twilio_account_sid"],
        auth_token=config["twilio_auth_token"],
        from_number=config["twilio_from_number"],
        to_number=config["twilio_to_number"],
        message=message
    )

    if success:
        logger.info("✅ Hava durumu uyarısı başarıyla gönderildi!")
    else:
        logger.error("❌ Hava durumu uyarısı gönderilemedi!")

    logger.info("=" * 60)


def main():
    """
    Komut satırı argümanlarını işler ve zamanlayıcıyı başlatır.
    """
    parser = argparse.ArgumentParser(
        description="Hava Durumu Uyarı Otomasyon Betiği",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python main.py          → Zamanlayıcı modunda çalıştır (her gün 08:30)
  python main.py --now    → Hemen bir kez çalıştır (test amaçlı)
        """
    )
    parser.add_argument(
        "--now",
        action="store_true",
        help="Zamanlayıcıyı atla, hemen bir kez çalıştır"
    )
    args = parser.parse_args()

    if args.now:
        # ─── Anlık çalıştırma (test için) ────────────────────────────────
        logger.info("Anlık test modu: Hava durumu kontrolü hemen çalıştırılıyor...")
        run_weather_check()
    else:
        # ─── Zamanlayıcı modu ────────────────────────────────────────────
        schedule.every().day.at("08:30").do(run_weather_check)

        logger.info("⏰ Zamanlayıcı başlatıldı. Her sabah saat 08:30'da çalışacak.")
        logger.info("   Durdurmak için Ctrl+C basın.")

        try:
            while True:
                schedule.run_pending()
                time.sleep(30)  # 30 saniyede bir kontrol et
        except KeyboardInterrupt:
            logger.info("Zamanlayıcı durduruldu.")


if __name__ == "__main__":
    main()
