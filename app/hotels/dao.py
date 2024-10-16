from datetime import date

from sqlalchemy import and_, func, or_, select

from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker, engine
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms
from app.logger import logger


class HotelDAO(BaseDAO):
    model = Hotels

    @classmethod
    async def find_all(cls, location: str, date_from: date, date_to: date):
        """
        Этот метод находит все доступные отели по заданной локации и датам.

        Использует CTE (Common Table Expression) для подсчета количества забронированных номеров:
        1. booked_rooms - выбирает идентификаторы комнат и подсчитывает количество забронированных комнат
        2. booked_hotels - подсчитывает количество доступных комнат в каждом отеле.

        Затем выбирает отели с оставшимися комнатами и подходящим местоположением.
        """
        # CTE для получения количества забронированных комнат
        booked_rooms = (
            select(Bookings.room_id, func.count(Bookings.room_id).label("rooms_booked"))
            .select_from(Bookings)
            .where(
                or_(
                    and_(
                        Bookings.date_from >= date_from,
                        Bookings.date_from <= date_to,
                    ),
                    and_(
                        Bookings.date_from <= date_from,
                        Bookings.date_to > date_from,
                    ),
                ),
            )
            .group_by(Bookings.room_id)
            .cte("booked_rooms")
        )

        # CTE для подсчета оставшихся комнат в отелях
        booked_hotels = (
            select(Rooms.hotel_id, func.sum(
                    Rooms.quantity - func.coalesce(booked_rooms.c.rooms_booked, 0)
            ).label("rooms_left"))
            .select_from(Rooms)
            .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)
            .group_by(Rooms.hotel_id)
            .cte("booked_hotels")
        )

        # Запрос для получения отелей с оставшимися комнатами
        get_hotels_with_rooms = (
            select(
                Hotels.__table__.columns,  # Получаем все столбцы модели Hotels
                booked_hotels.c.rooms_left,  # Добавляем оставшиеся комнаты
            )
            .join(booked_hotels, booked_hotels.c.hotel_id == Hotels.id, isouter=True)
            .where(
                and_(
                    booked_hotels.c.rooms_left > 0,  # Условие: оставшиеся комнаты должны быть больше 0
                    Hotels.location.like(f"%{location}%"),  # Фильтр по местоположению
                )
            )
        )

        async with async_session_maker() as session:
            # Логирование скомпилированного запроса для отладки (при необходимости)
            # logger.debug(get_hotels_with_rooms.compile(engine, compile_kwargs={"literal_binds": True}))
            # Выполняем запрос и возвращаем результаты
            hotels_with_rooms = await session.execute(get_hotels_with_rooms)
            return hotels_with_rooms.mappings().all()
