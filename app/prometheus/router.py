import time
from random import random

from fastapi import APIRouter

# Создание экземпляра APIRouter для маршрутов тестирования
router = APIRouter(
    prefix="/prometheus",  # Префикс для всех маршрутов в этом роутере
    tags=["Тестирование Grafana + Prometheus"]  # Тэги для группировки маршрутов в документации
)

# Эндпоинт, который случайным образом вызывает исключение
@router.get("/get_error")
def get_error():
    if random() > 0.5:  # Генерирует случайное число от 0 до 1
        raise ZeroDivisionError  # Случайная ошибка деления на ноль
    else:
        raise KeyError  # Случайная ошибка ключа

# Эндпоинт, который имитирует задержку обработки
@router.get("/time_consumer")
def time_consumer():
    time.sleep(random() * 5)  # Задержка от 0 до 5 секунд
    return 1  # Возвращает 1 после задержки

# Эндпоинт, который потребляет значительное количество памяти
@router.get("/memory_consumer")
def memory_consumer():
    _ = [i for i in range(30_000_000)]  # Создает список с 30 миллионами элементов
    return 1  # Возвращает 1 после завершения потребления памяти
