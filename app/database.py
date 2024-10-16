from sqlalchemy import NullPool  # Импорт NullPool для отключения пула соединений
from sqlalchemy.ext.asyncio import create_async_engine  # Импорт функции для создания асинхронного движка базы данных
from sqlalchemy.orm import DeclarativeBase  # Импорт базового класса для декларативного объявления моделей
from sqlalchemy.ext.asyncio import async_sessionmaker  # Импорт функции для создания асинхронных сессий

from app.config import settings  # Импорт настроек приложения

# Определяем URL базы данных и параметры в зависимости от режима работы приложения
if settings.MODE == "TEST":
    # Если режим тестирования, используем тестовую базу данных
    DATABASE_URL = settings.TEST_DATABASE_URL
    # Устанавливаем параметры пула соединений для тестирования
    DATABASE_PARAMS = {"poolclass": NullPool}  # NullPool отключает пул соединений
else:
    # В остальных режимах используем основную базу данных
    DATABASE_URL = settings.DATABASE_URL
    DATABASE_PARAMS = {}  # Без дополнительных параметров пула соединений

# Создаем асинхронный движок базы данных с использованием заданного URL и параметров
engine = create_async_engine(DATABASE_URL, **DATABASE_PARAMS)

# Во 2.0 версии SQLAlchemy был добавлен async_sessionmaker для работы с асинхронными сессиями.
# Создаем фабрику асинхронных сессий, которая будет использовать движок
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

# Определяем базовый класс для всех моделей, использующих декларативный стиль
class Base(DeclarativeBase):
    pass  # Класс не содержит дополнительной логики, служит основой для других моделей
