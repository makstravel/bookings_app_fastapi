from datetime import date
from sqlalchemy import and_, func, or_, select

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.hotels.rooms.models import Rooms
from app.logger import logger


class RoomDAO(BaseDAO):
    model = Rooms

    @classmethod
    async def find_all(cls, hotel_id: int, date_from: date, date_to: date):
        """
        Получить доступные номера в отеле на указанные даты.

        Используется CTE (Common Table Expression) для определения забронированных номеров,
        а затем возвращается список доступных номеров с подсчетом оставшихся мест.
        """

        # Создание CTE для получения количества забронированных номеров
        booked_rooms = (
            select(Bookings.room_id, func.count(Bookings.room_id).label("rooms_booked"))
            .select_from(Bookings)  # Выбор из таблицы бронирований
            .where(
                or_(
                    and_(
                        Bookings.date_from >= date_from,  # Начало бронирования после запрашиваемых дат
                        Bookings.date_from <= date_to,  # Конец бронирования до запрашиваемых дат
                    ),
                    and_(
                        Bookings.date_from <= date_from,  # Начало бронирования до запрашиваемых дат
                        Bookings.date_to > date_from,  # Конец бронирования после начала запрашиваемых дат
                    ),
                ),
            )
            .group_by(Bookings.room_id)  # Группировка по ID номера
            .cte("booked_rooms")  # Создание CTE с именем "booked_rooms"
        )

        # Запрос для получения информации о доступных номерах в отеле
        get_rooms = (
            select(
                Rooms.__table__.columns,  # Все столбцы из таблицы номеров
                (Rooms.price * (date_to - date_from).days).label("total_cost"),  # Общая стоимость
                (Rooms.quantity - func.coalesce(booked_rooms.c.rooms_booked, 0)).label("rooms_left"),  # Остаток номеров
            )
            .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)  # Соединение с CTE
            .where(
                Rooms.hotel_id == hotel_id  # Фильтрация по ID отеля
            )
        )

        # Открытие асинхронной сессии для выполнения запроса
        async with async_session_maker() as session:
            # Для отладки можно вывести SQL-запрос в лог
            # logger.debug(get_rooms.compile(engine, compile_kwargs={"literal_binds": True}))
            rooms = await session.execute(get_rooms)  # Выполнение запроса
            return rooms.mappings().all()  # Возврат всех найденных записей
