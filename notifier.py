"""
notifier.py — Twilio WhatsApp API ile bildirim gönderme modülü.

Twilio'nun WhatsApp Sandbox veya üretim ortamı üzerinden
WhatsApp mesajları gönderir.
"""

from twilio.rest import Client
import logging

logger = logging.getLogger(__name__)


def send_whatsapp_message(
    account_sid: str,
    auth_token: str,
    from_number: str,
    to_number: str,
    message: str
) -> bool:
    """
    Twilio API kullanarak WhatsApp mesajı gönderir.

    Args:
        account_sid: Twilio Account SID
        auth_token: Twilio Auth Token
        from_number: Twilio WhatsApp numarası (örn: "whatsapp:+14155238886")
        to_number: Alıcı WhatsApp numarası (örn: "whatsapp:+905xxxxxxxxx")
        message: Gönderilecek mesaj metni

    Returns:
        True: Mesaj başarıyla gönderildiyse
        False: Mesaj gönderilemezse
    """
    try:
        client = Client(account_sid, auth_token)

        msg = client.messages.create(
            from_=from_number,
            body=message,
            to=to_number
        )

        logger.info(f"WhatsApp mesajı gönderildi! SID: {msg.sid}, Durum: {msg.status}")
        return True

    except Exception as e:
        logger.error(f"WhatsApp mesajı gönderilemedi: {e}")
        return False
