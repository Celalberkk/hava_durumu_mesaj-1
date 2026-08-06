"""
alerts.py — Hava durumu koşullarını kontrol edip uyarı mesajı oluşturma modülü.

Saatlik hava durumu verisini analiz eder ve aşağıdaki koşulları kontrol eder:
- Yağmur riski (yağış olasılığı > 0%)
- Yüksek sıcaklık (>= 35°C)
- Düşük sıcaklık (<= 10°C)
"""

import logging

logger = logging.getLogger(__name__)

# Varsayılan eşik değerleri
DEFAULT_HIGH_TEMP = 35  # °C
DEFAULT_LOW_TEMP = 10   # °C
DEFAULT_RAIN_THRESHOLD = 20  # % (yağış olasılığı eşiği)


def check_rain_risk(hourly_data: list[dict], threshold: int = DEFAULT_RAIN_THRESHOLD) -> list[dict]:
    """
    Yağmur ihtimali olan saatleri tespit eder.

    Args:
        hourly_data: Saatlik hava durumu verileri listesi
        threshold: Yağış olasılığı eşiği (varsayılan: %20)

    Returns:
        Yağmur riski olan saatlerin listesi.
        Her eleman: {"hour": "15:00", "probability": 45}
    """
    rain_hours = []
    for entry in hourly_data:
        prob = entry.get("precipitation_probability", 0)
        if prob >= threshold:
            rain_hours.append({
                "hour": entry["hour"],
                "probability": prob
            })

    if rain_hours:
        logger.info(f"Yağmur riski tespit edilen saat sayısı: {len(rain_hours)}")
    return rain_hours


def check_high_temp(hourly_data: list[dict], threshold: float = DEFAULT_HIGH_TEMP) -> list[dict]:
    """
    Sıcaklığın eşiğin üzerine çıktığı saatleri tespit eder.

    Args:
        hourly_data: Saatlik hava durumu verileri listesi
        threshold: Sıcaklık eşiği (varsayılan: 35°C)

    Returns:
        Yüksek sıcaklık olan saatlerin listesi.
        Her eleman: {"hour": "13:00", "temperature": 37.2}
    """
    hot_hours = []
    for entry in hourly_data:
        temp = entry.get("temperature", 0)
        if temp >= threshold:
            hot_hours.append({
                "hour": entry["hour"],
                "temperature": temp
            })

    if hot_hours:
        logger.info(f"Yüksek sıcaklık tespit edilen saat sayısı: {len(hot_hours)}")
    return hot_hours


def check_low_temp(hourly_data: list[dict], threshold: float = DEFAULT_LOW_TEMP) -> list[dict]:
    """
    Sıcaklığın eşiğin altına düştüğü saatleri tespit eder.

    Args:
        hourly_data: Saatlik hava durumu verileri listesi
        threshold: Sıcaklık eşiği (varsayılan: 10°C)

    Returns:
        Düşük sıcaklık olan saatlerin listesi.
        Her eleman: {"hour": "22:00", "temperature": 7.5}
    """
    cold_hours = []
    for entry in hourly_data:
        temp = entry.get("temperature", 0)
        if temp <= threshold:
            cold_hours.append({
                "hour": entry["hour"],
                "temperature": temp
            })

    if cold_hours:
        logger.info(f"Düşük sıcaklık tespit edilen saat sayısı: {len(cold_hours)}")
    return cold_hours


def _format_hour_range(hours: list[str]) -> str:
    """
    Ardışık saatleri aralık formatına dönüştürür.
    Örn: ["14:00", "15:00", "16:00"] → "14:00 - 17:00"
    Örn: ["09:00"] → "09:00 - 10:00"
    """
    if not hours:
        return ""

    # Saatleri sırala
    sorted_hours = sorted(hours)

    # Ardışık saat gruplarını bul
    ranges = []
    start = sorted_hours[0]
    prev_val = int(start.split(":")[0])

    for i in range(1, len(sorted_hours)):
        curr_val = int(sorted_hours[i].split(":")[0])
        if curr_val != prev_val + 1:
            # Aralık sonlandı
            end_val = prev_val + 1
            ranges.append(f"{start} - {end_val:02d}:00")
            start = sorted_hours[i]
        prev_val = curr_val

    # Son aralığı ekle
    end_val = prev_val + 1
    if end_val >= 24:
        ranges.append(f"{start} - 00:00")
    else:
        ranges.append(f"{start} - {end_val:02d}:00")

    return ", ".join(ranges)


def build_alert_message(
    rain_hours: list[dict],
    hot_hours: list[dict],
    cold_hours: list[dict],
    city: str = "",
    hourly_data: "list[dict] | None" = None
) -> str:
    """
    Tespit edilen koşullara göre Türkçe uyarı mesajı oluşturur.
    Hiçbir uyarı yoksa günün sıcaklık aralığını içeren normal hava mesajı döndürür.

    Args:
        rain_hours: Yağmur riski olan saatler
        hot_hours: Yüksek sıcaklık olan saatler
        cold_hours: Düşük sıcaklık olan saatler
        city: Konum şehir adı (mesajda gösterilir)
        hourly_data: Saatlik hava durumu verileri (normal hava mesajı için gerekli)

    Returns:
        Formatlanmış uyarı mesajı metni
    """
    has_alerts = rain_hours or hot_hours or cold_hours

    city_label = f" ({city})" if city else ""
    lines = [f"☀️ *Günaydın! Bugünkü hava durumu uyarınız{city_label}:*\n"]

    if not has_alerts:
        # Günün en düşük ve en yüksek sıcaklığını hesapla
        if hourly_data:
            temps = [entry["temperature"] for entry in hourly_data]
            min_temp = min(temps)
            max_temp = max(temps)
            lines.append(
                f"✅ Bugün uyarı gerektiren ekstrem bir hava durumu yok. "
                f"Hava genelde {min_temp:.0f}°C - {max_temp:.0f}°C civarlarında "
                f"seyredecek. Güzel bir gün dilerim! 🌤️"
            )
        else:
            lines.append(
                "✅ Bugün hava durumunda dikkat edilmesi gereken "
                "önemli bir durum yok. Güzel bir gün geçirin! 🌤️"
            )
        return "\n".join(lines)

    # ☔ Yağmur uyarısı
    if rain_hours:
        hours_list = [r["hour"] for r in rain_hours]
        time_range = _format_hour_range(hours_list)
        avg_prob = sum(r["probability"] for r in rain_hours) // len(rain_hours)
        max_prob = max(r["probability"] for r in rain_hours)

        lines.append(
            f"☔ *Yağmur Riski:* {time_range} arasında yağmur ihtimali var "
            f"(ort. %{avg_prob}, maks. %{max_prob}). "
            f"Yanınıza şemsiye almayı unutmayın!"
        )

    # 🔴 Yüksek sıcaklık uyarısı
    if hot_hours:
        hours_list = [h["hour"] for h in hot_hours]
        time_range = _format_hour_range(hours_list)
        max_temp = max(h["temperature"] for h in hot_hours)

        lines.append(
            f"🔴 *Yüksek Sıcaklık:* {time_range} arası sıcaklık "
            f"{DEFAULT_HIGH_TEMP}°C üstünde olacak (maks. {max_temp:.1f}°C). "
            f"Bol su için ve güneşten korunun!"
        )

    # 🔵 Düşük sıcaklık uyarısı
    if cold_hours:
        hours_list = [c["hour"] for c in cold_hours]
        time_range = _format_hour_range(hours_list)
        min_temp = min(c["temperature"] for c in cold_hours)

        lines.append(
            f"🔵 *Düşük Sıcaklık:* {time_range} arası sıcaklık "
            f"{DEFAULT_LOW_TEMP}°C altına düşecek (min. {min_temp:.1f}°C). "
            f"Kalın giyinmeyi unutmayın!"
        )

    return "\n\n".join(lines)
