from email.message import EmailMessage
from pydantic import EmailStr

from app.config import settings

def create_booking_confirmation_template(
    booking: dict,
    email_to: EmailStr,
):
    # Создание нового сообщения электронной почты
    email = EmailMessage()

    # Установка темы письма
    email["Subject"] = "Подтверждение бронирования"
    # Установка адреса отправителя
    email["From"] = settings.SMTP_USER
    # Установка адреса получателя
    email["To"] = email_to

    # Установка содержания письма в формате HTML
    email.set_content(
        f"""
            <h1>Подтвердите бронирование</h1>
            Вы забронировали отель с {booking["date_from"]} по {booking["date_to"]}
        """,
        subtype="html"  # Указывает, что содержание является HTML
    )
    return email  # Возвращает объект сообщения электронной почты
