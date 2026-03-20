from src.database import Customer
from .send_email import send_email


async def send_welcome_email(customer: Customer) -> None:
    await send_email(
        recipient=customer.email,
        subject="Welcome to Auto Market!",
        body=f"Dear {customer.username},\n\nWelcome to Auto Market!",
    )
