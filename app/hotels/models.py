from sqlalchemy import JSON, Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Hotels(Base):
    __tablename__ = "hotels"  # Указывает имя таблицы в базе данных

    id = Column(Integer, primary_key=True)  # Уникальный идентификатор отеля
    name = Column(String, nullable=False)  # Название отеля, не может быть пустым
    location = Column(String, nullable=False)  # Расположение отеля, не может быть пустым
    services = Column(JSON)  # Услуги, предоставляемые отелем (хранится в формате JSON)
    rooms_quantity = Column(Integer, nullable=False)  # Общее количество номеров в отеле
    image_id = Column(Integer)  # Идентификатор изображения отеля

    # Определяет связь "один ко многим" с таблицей Rooms
    rooms = relationship("Rooms", back_populates="hotel")

    def __str__(self):
        # Строковое представление отеля, отображающее название и первые 30 символов местоположения
        return f"Отель {self.name} {self.location[:30]}"
