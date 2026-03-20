from email.message import EmailMessage

import aiosmtplib

from src.core.config import settings


async def send_email(recipient: str, subject: str, body: str) -> None:
    message = EmailMessage()
    message["From"] = settings.email.FROM_EMAIL
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        sender=settings.email.FROM_EMAIL,
        recipients=[recipient],
        hostname=settings.email.HOST,
        port=settings.email.PORT,
        use_tls=settings.email.USE_TLS,
        username=settings.email.HOST_USER if settings.email.HOST_USER else None,
        password=settings.email.HOST_PASSWORD if settings.email.HOST_PASSWORD else None,
    )
