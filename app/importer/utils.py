import datetime
import json
from typing import Iterable

from app.bookings.dao import BookingDAO
from app.hotels.dao import HotelDAO
from app.hotels.rooms.dao import RoomDAO
from app.logger import logger

# Сопоставление имен таблиц с соответствующими DAO
TABLE_MODEL_MAP = {
    "hotels": HotelDAO,
    "rooms": RoomDAO,
    "bookings": BookingDAO,
}

def convert_csv_to_postgres_format(csv_iterable: Iterable):
    """
    Преобразует данные из CSV в формат, подходящий для вставки в PostgreSQL.

    Args:
        csv_iterable (Iterable): Итерабельный объект (например, DictReader),
                                 содержащий строки CSV в виде словарей.

    Returns:
        list: Список преобразованных строк в формате, подходящем для PostgreSQL.

    Raises:
        Exception: Логирует ошибку, если преобразование невозможно.
    """
    try:
        data = []  # Инициализация списка для хранения преобразованных данных
        for row in csv_iterable:  # Проходим по каждой строке в итерабельном объекте
            for k, v in row.items():  # Проходим по ключам и значениям строки
                # Если значение является числом, преобразуем его в int
                if v.isdigit():
                    row[k] = int(v)
                # Если ключ - это 'services', парсим строку JSON
                elif k == "services":
                    row[k] = json.loads(v.replace("'", '"'))
                # Если ключ содержит 'date', преобразуем строку в datetime
                elif "date" in k:
                    row[k] = datetime.datetime.strptime(v, "%Y-%m-%d")
            data.append(row)  # Добавляем преобразованную строку в список
        return data  # Возвращаем список преобразованных строк
    except Exception:
        # Логируем ошибку, если что-то пошло не так при преобразовании
        logger.error("Cannot convert CSV into DB format", exc_info=True)
