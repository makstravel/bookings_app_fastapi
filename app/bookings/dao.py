# Импортируем необходимые модули для работы с датами и SQL-запросами.
from datetime import date
from sqlalchemy import and_, func, insert, or_, select
from sqlalchemy.exc import SQLAlchemyError

# Импортируем модели и вспомогательные модули из приложения.
from app.bookings.models import Bookings
from app.dao.base import BaseDAO
from app.database import async_session_maker
from app.exceptions import RoomFullyBooked
from app.hotels.rooms.models import Rooms
from app.logger import logger


# DAO (Data Access Object) для работы с бронированиями.
class BookingDAO(BaseDAO):
    # Указываем модель для взаимодействия.
    model = Bookings

    # Асинхронный метод для получения всех бронирований пользователя с информацией о номере.
    @classmethod
    async def find_all_with_images(cls, user_id: int):
        async with async_session_maker() as session:
            # Формируем SQL-запрос для получения бронирований и связанных с ними номеров.
            query = (
                select(
                    # Используем __table__.columns, чтобы избежать вложенности при выводе данных из SQLAlchemy.
                    Bookings.__table__.columns,
                    Rooms.__table__.columns,
                )
                # Выполняем внешнее объединение таблицы бронирований с таблицей номеров.
                .join(Rooms, Rooms.id == Bookings.room_id, isouter=True)
                # Условие фильтрации по user_id для поиска бронирований конкретного пользователя.
                .where(Bookings.user_id == user_id)
            )
            # Выполняем запрос и возвращаем результаты в виде сопоставлений.
            result = await session.execute(query)
            return result.mappings().all()

    # Асинхронный метод для добавления бронирования.
    @classmethod
    async def add(
        cls,
        user_id: int,
        room_id: int,
        date_from: date,
        date_to: date,
    ):
        """
        Выполняет проверку наличия свободных номеров на указанные даты и добавляет бронирование,
        если номер доступен.

        SQL-запрос для проверки наличия свободных номеров:
        WITH booked_rooms AS (
            SELECT * FROM bookings
            WHERE room_id = 1 AND
                (date_from >= '2023-05-15' AND date_from <= '2023-06-20') OR
                (date_from <= '2023-05-15' AND date_to > '2023-05-15')
        )
        SELECT rooms.quantity - COUNT(booked_rooms.room_id) FROM rooms
        LEFT JOIN booked_rooms ON booked_rooms.room_id = rooms.id
        WHERE rooms.id = 1
        GROUP BY rooms.quantity, booked_rooms.room_id
        """
        try:
            async with async_session_maker() as session:
                # Формируем CTE (Common Table Expression) для получения уже забронированных номеров.
                booked_rooms = (
                    select(Bookings)
                    .where(
                        and_(
                            Bookings.room_id == room_id,
                            or_(
                                # Проверяем, что бронирование пересекается с уже существующими бронированиями.
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
                    )
                    .cte("booked_rooms")  # Создаем CTE подзапрос.
                )

                # Формируем запрос для проверки оставшихся свободных номеров.
                get_rooms_left = (
                    select(
                        # Вычисляем количество свободных номеров.
                        (Rooms.quantity - func.count(booked_rooms.c.room_id)).label(
                            "rooms_left"
                        )
                    )
                    .select_from(Rooms)
                    # Объединяем таблицы rooms и забронированных номеров через CTE.
                    .join(booked_rooms, booked_rooms.c.room_id == Rooms.id, isouter=True)
                    .where(Rooms.id == room_id)
                    # Группируем результат по количеству номеров.
                    .group_by(Rooms.quantity, booked_rooms.c.room_id)
                )

                # Выполняем запрос для получения количества оставшихся номеров.
                rooms_left = await session.execute(get_rooms_left)
                rooms_left: int = rooms_left.scalar()  # Преобразуем результат в int.

                logger.debug(f"{rooms_left=}")  # Логируем количество оставшихся номеров.

                # Если есть свободные номера, продолжаем создание бронирования.
                if rooms_left > 0:
                    # Запрашиваем цену номера.
                    get_price = select(Rooms.price).filter_by(id=room_id)
                    price = await session.execute(get_price)
                    price: int = price.scalar()

                    # Формируем запрос на вставку нового бронирования.
                    add_booking = (
                        insert(Bookings)
                        .values(
                            room_id=room_id,
                            user_id=user_id,
                            date_from=date_from,
                            date_to=date_to,
                            price=price,
                        )
                        # Возвращаем информацию о созданном бронировании.
                        .returning(
                            Bookings.id,
                            Bookings.user_id,
                            Bookings.room_id,
                            Bookings.date_from,
                            Bookings.date_to,
                        )
                    )

                    # Выполняем запрос на добавление нового бронирования.
                    new_booking = await session.execute(add_booking)
                    await session.commit()  # Подтверждаем изменения в базе данных.
                    return new_booking.mappings().one()  # Возвращаем результат.
                else:
                    # Если номеров нет, вызываем исключение RoomFullyBooked.
                    raise RoomFullyBooked
        except RoomFullyBooked:
            # Если комната полностью забронирована, повторно вызываем исключение.
            raise RoomFullyBooked
        except (SQLAlchemyError, Exception) as e:
            # Обработка исключений. SQLAlchemyError — ошибки базы данных, Exception — другие ошибки.
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot add booking"
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Cannot add booking"
            # Логируем ошибку с дополнительной информацией.
            extra = {
                "user_id": user_id,
                "room_id": room_id,
                "date_from": date_from,
                "date_to": date_to,
            }
            logger.error(msg, extra=extra, exc_info=True)
