from pathlib import Path

from starlette.templating import Jinja2Templates

from src.core.config import settings
from .send_email import send_email

_TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates"
templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))


async def send_password_reset_email(to_email: str, username: str, token: str) -> None:
    reset_url = f"{settings.email.frontend_url}/reset-password?token={token}"
    template = templates.env.get_template("email/password_reset.html")
    html_content = template.render(reset_url=reset_url, username=username)
    plain_text = f"""Hi {username},

You requested to reset your password. Click the link below to set a new password:

{reset_url}

This link will expire in 1 hour.

If you didn't request this, you can safely ignore this email.

Best regards,
The Auto Market Team
"""

    await send_email(
        recipient=to_email, subject="Reset Your Password - Auto Market", body=plain_text, html_content=html_content
    )
