"""
notifier.py — CallMeBot API ile bildirim gönderme modülü.

CallMeBot üzerinden 24 saat sınırına takılmadan
ücretsiz WhatsApp mesajları gönderir.
"""

import requests
import logging

logger = logging.getLogger(__name__)

def send_whatsapp_message(phone_number: str, api_key: str, message: str) -> bool:
    """
    CallMeBot API kullanarak WhatsApp mesajı gönderir.

    Args:
        phone_number: Alıcı WhatsApp numarası (Başında + ile ülke kodu, boşluksuz. Örn: +905xxxxxxxxx)
        api_key: CallMeBot'tan alınan 6 haneli şifre
        message: Gönderilecek mesaj metni

    Returns:
        True: Mesaj başarıyla gönderildiyse
        False: Mesaj gönderilemezse
    """
    try:
        url = "https://api.callmebot.com/whatsapp.php"
        params = {
            "phone": phone_number,
            "text": message,
            "apikey": api_key
        }
        
        response = requests.get(url, params=params, timeout=15)
        
        # 200 OK döndüyse mesaj gitmiştir
        if response.status_code == 200:
            logger.info("WhatsApp mesajı CallMeBot ile başarıyla gönderildi!")
            return True
        else:
            logger.error(f"CallMeBot hatası (Kod: {response.status_code}): {response.text}")
            return False

    except Exception as e:
        logger.error(f"WhatsApp mesajı gönderilirken bağlantı hatası oluştu: {e}")
        return False
