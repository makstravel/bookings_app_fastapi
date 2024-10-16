import time  # Импортируем модуль time для измерения времени обработки запросов

import sentry_sdk  # Импортируем Sentry SDK для мониторинга и отслеживания ошибок
from fastapi import FastAPI, Request  # Импортируем класс FastAPI и объект Request
from fastapi.middleware.cors import CORSMiddleware  # Импортируем middleware для CORS
from fastapi.staticfiles import StaticFiles  # Импортируем для обслуживания статических файлов
from fastapi_cache import FastAPICache  # Импортируем библиотеку для кэширования
from fastapi_cache.backends.redis import RedisBackend  # Импортируем бэкенд Redis для кэширования
from fastapi_versioning import VersionedFastAPI  # Импортируем для управления версиями API
from prometheus_fastapi_instrumentator import Instrumentator  # Импортируем инструментатор для Prometheus
from redis import asyncio as aioredis  # Импортируем асинхронный Redis клиент
from sqladmin import Admin  # Импортируем административный интерфейс для SQLAlchemy

# Импортируем зависимости из вашего приложения
from app.admin.auth import authentication_backend
from app.admin.views import BookingsAdmin, HotelsAdmin, RoomsAdmin, UsersAdmin
from app.bookings.router import router as router_bookings
from app.config import settings
from app.database import engine
from app.hotels.router import router as router_hotels
from app.images.router import router as router_images
from app.importer.router import router as router_import
from app.logger import logger
from app.pages.router import router as router_pages
from app.prometheus.router import router as router_prometheus
from app.users.router import router_auth, router_users

# Создаем экземпляр приложения FastAPI
app = FastAPI(
    title="Бронирование Отелей",  # Указываем название приложения
    version="0.1.0",  # Указываем версию приложения
    root_path="/api",  # Определяем корневой путь для API
)

# Проверяем, не находится ли приложение в тестовом режиме
if settings.MODE != "TEST":
    # Подключение Sentry для мониторинга ошибок, отключаем для локального тестирования
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,  # Указываем DSN для подключения к Sentry
        traces_sample_rate=1.0,  # Устанавливаем уровень трассировки
    )

# Включение основных роутеров для обработки запросов
app.include_router(router_auth)  # Роутер для аутентификации пользователей
app.include_router(router_users)  # Роутер для управления пользователями
app.include_router(router_hotels)  # Роутер для управления отелями
app.include_router(router_bookings)  # Роутер для управления бронированиями

# Включение дополнительных роутеров
app.include_router(router_images)  # Роутер для работы с изображениями
app.include_router(router_prometheus)  # Роутер для метрик Prometheus
app.include_router(router_import)  # Роутер для импорта данных

# Конфигурация CORS, чтобы разрешить запросы из браузера
origins = [
    # Разрешаем запросы с фронтенда, работающего на порту 3000
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,  # Подключаем CORS Middleware
    allow_origins=origins,  # Разрешенные источники
    allow_credentials=True,  # Разрешаем использование учетных данных
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],  # Разрешенные методы
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers",
                   "Access-Control-Allow-Origin",
                   "Authorization"],  # Разрешенные заголовки
)

# Подключение версионирования для API
app = VersionedFastAPI(app,
    version_format='{major}',  # Формат версии
    prefix_format='/api/v{major}',  # Формат префикса для версии
)

app.include_router(router_pages)  # Включаем роутер для страниц

# Проверка, находимся ли мы в тестовом режиме
if settings.MODE == "TEST":
    # При тестировании необходимо подключать Redis для корректной работы кэширования
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="cache")  # Инициализация кэширования с Redis

@app.on_event("startup")
def startup():
    # Устанавливаем соединение с Redis при старте приложения
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="cache")  # Инициализация кэширования

# Подключение эндпоинта для отображения метрик, собираемых Prometheus
instrumentator = Instrumentator(
    should_group_status_codes=False,  # Не группируем статус-коды
    excluded_handlers=[".*admin.*", "/metrics"],  # Исключаем админку и метрики из группировки
)
instrumentator.instrument(app).expose(app)  # Инструментируем приложение и открываем доступ к метрикам

# Подключение административного интерфейса
admin = Admin(app, engine, authentication_backend=authentication_backend)  # Создаем админку
admin.add_view(UsersAdmin)  # Добавляем представление для управления пользователями
admin.add_view(HotelsAdmin)  # Добавляем представление для управления отелями
admin.add_view(RoomsAdmin)  # Добавляем представление для управления номерами
admin.add_view(BookingsAdmin)  # Добавляем представление для управления бронированиями

# Настройка обслуживания статических файлов
app.mount("/static", StaticFiles(directory="app/static"), "static")  # Подключаем статические файлы

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()  # Запоминаем время начала обработки запроса
    response = await call_next(request)  # Обрабатываем запрос и ждем ответа
    process_time = time.time() - start_time  # Вычисляем время обработки
    # Логируем время обработки запроса
    logger.info("Request handling time", extra={
        "process_time": round(process_time, 4)  # Округляем до 4 знаков после запятой
    })
    return response  # Возвращаем ответ

# Примечание: конфигурация FastAPI происходит в одном файле, что может усложнить поддержку.
