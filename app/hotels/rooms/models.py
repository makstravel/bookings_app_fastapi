from sqlalchemy import JSON, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Rooms(Base):
    __tablename__ = "rooms"  # Название таблицы в базе данных

    # Основные поля таблицы
    id = Column(Integer, primary_key=True, nullable=False)  # Уникальный идентификатор номера
    hotel_id = Column(ForeignKey("hotels.id"), nullable=False)  # Идентификатор отеля (внешний ключ)
    name = Column(String, nullable=False)  # Название номера
    description = Column(String, nullable=True)  # Описание номера
    price = Column(Integer, nullable=False)  # Цена за ночь
    services = Column(JSON, nullable=True)  # Список услуг (в формате JSON)
    quantity = Column(Integer, nullable=False)  # Количество доступных номеров данного типа
    image_id = Column(Integer)  # Идентификатор изображения номера (если имеется)

    # Связи с другими моделями
    hotel = relationship("Hotels", back_populates="rooms")  # Связь с моделью Hotels
    booking = relationship("Bookings", back_populates="room")  # Связь с моделью Bookings

    def __str__(self):
        return f"Номер {self.name}"  # Человекочитаемое представление номера
