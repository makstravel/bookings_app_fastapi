from celery import Celery

from app.config import settings

# Инициализация экземпляра Celery с именем "tasks"
celery = Celery(
    "tasks",  # Имя приложения
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",  # URL брокера Redis
    include=["app.tasks.tasks"]  # Модули, которые Celery будет загружать и искать задачи
)
