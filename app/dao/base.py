# Импортируем необходимые функции для работы с запросами SQLAlchemy.
from sqlalchemy import delete, insert, select
from sqlalchemy.exc import SQLAlchemyError

# Импортируем асинхронный менеджер сессий и логгер для записи ошибок.
from app.database import async_session_maker
from app.logger import logger


# Базовый класс DAO (Data Access Object), который предоставляет общие методы
# для взаимодействия с базой данных.
class BaseDAO:
    model = None  # Атрибут, который должен быть определен в дочерних классах (модель таблицы).

    # Метод для поиска одной записи по указанным фильтрам или возвращения None, если запись не найдена.
    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session_maker() as session:
            # Создаем SQL-запрос на выборку данных с фильтрацией по переданным аргументам.
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            # Возвращаем одну запись или None, если запись не найдена.
            return result.mappings().one_or_none()

    # Метод для поиска всех записей по указанным фильтрам.
    @classmethod
    async def find_all(cls, **filter_by):
        async with async_session_maker() as session:
            # Создаем SQL-запрос на выборку всех данных с фильтрацией по переданным аргументам.
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            # Возвращаем все найденные записи.
            return result.mappings().all()

    # Метод для добавления новой записи в базу данных.
    @classmethod
    async def add(cls, **data):
        try:
            # Формируем SQL-запрос для вставки новой записи и возврата её ID.
            query = insert(cls.model).values(**data).returning(cls.model.id)
            async with async_session_maker() as session:
                # Выполняем запрос и коммитим изменения в базу.
                result = await session.execute(query)
                await session.commit()
                # Возвращаем первую запись (ID новой записи).
                return result.mappings().first()
        except (SQLAlchemyError, Exception) as e:
            # Обработка исключений, возникающих при работе с базой данных.
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc: Cannot insert data into table"
            elif isinstance(e, Exception):
                msg = "Unknown Exc: Cannot insert data into table"

            # Логируем ошибку с указанием названия таблицы и информации об исключении.
            logger.error(msg, extra={"table": cls.model.__tablename__}, exc_info=True)
            return None

    # Метод для удаления записей, удовлетворяющих указанным условиям.
    @classmethod
    async def delete(cls, **filter_by):
        async with async_session_maker() as session:
            # Формируем SQL-запрос на удаление данных с фильтрацией по переданным аргументам.
            query = delete(cls.model).filter_by(**filter_by)
            # Выполняем запрос и коммитим изменения в базу.
            await session.execute(query)
            await session.commit()

    # Метод для массового добавления нескольких записей в базу данных.
    @classmethod
    async def add_bulk(cls, *data):
        # Метод принимает список данных и добавляет их в базу данных через позиционные аргументы (*data).
        try:
            # Формируем SQL-запрос для массовой вставки данных и возврата ID.
            query = insert(cls.model).values(*data).returning(cls.model.id)
            async with async_session_maker() as session:
                # Выполняем запрос и коммитим изменения.
                result = await session.execute(query)
                await session.commit()
                # Возвращаем первую запись (ID первой добавленной записи).
                return result.mappings().first()
        except (SQLAlchemyError, Exception) as e:
            # Обработка исключений при массовом добавлении данных.
            if isinstance(e, SQLAlchemyError):
                msg = "Database Exc"
            elif isinstance(e, Exception):
                msg = "Unknown Exc"
            msg += ": Cannot bulk insert data into table"

            # Логируем ошибку с указанием таблицы и информации об исключении.
            logger.error(msg, extra={"table": cls.model.__tablename__}, exc_info=True)
            return None
