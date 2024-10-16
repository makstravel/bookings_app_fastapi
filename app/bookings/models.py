# Импортируем необходимые модули из SQLAlchemy для создания колонок, вычисляемых значений, типов данных и связей.
from sqlalchemy import Column, Computed, Date, ForeignKey, Integer
from sqlalchemy.orm import relationship

# Импортируем базовый класс модели базы данных.
from app.database import Base


# Модель бронирований в базе данных.
class Bookings(Base):
    # Указываем имя таблицы в базе данных.
    __tablename__ = "bookings"

    # Определяем колонки для таблицы бронирований.

    # Идентификатор бронирования (первичный ключ).
    id = Column(Integer, primary_key=True)

    # Внешний ключ, указывающий на идентификатор комнаты.
    room_id = Column(ForeignKey("rooms.id"))

    # Внешний ключ, указывающий на идентификатор пользователя.
    user_id = Column(ForeignKey("users.id"))

    # Дата начала бронирования, обязательное поле.
    date_from = Column(Date, nullable=False)

    # Дата окончания бронирования, обязательное поле.
    date_to = Column(Date, nullable=False)

    # Цена за день проживания, обязательное поле.
    price = Column(Integer, nullable=False)

    # Вычисляемая колонка, представляющая общую стоимость бронирования.
    # Общая стоимость вычисляется как разница между датами (количество дней) умноженная на цену за день.
    total_cost = Column(Integer, Computed("(date_to - date_from) * price"))

    # Вычисляемая колонка, представляющая количество дней бронирования.
    total_days = Column(Integer, Computed("date_to - date_from"))

    # Связь с пользователем. Связывает бронирование с моделью пользователей.
    user = relationship("Users", back_populates="booking")

    # Связь с комнатой. Связывает бронирование с моделью комнат.
    room = relationship("Rooms", back_populates="booking")

    # Метод для представления объекта бронирования в строковом формате.
    def __str__(self):
        return f"Booking #{self.id}"
