from datetime import date, datetime, timedelta
from typing import List

from fastapi import Query

from app.hotels.rooms.dao import RoomDAO
from app.hotels.rooms.schemas import SRoomInfo
from app.hotels.router import router


@router.get("/{hotel_id}/rooms")
# Этот эндпоинт предоставляет информацию о доступных номерах в указанном отеле
# по заданным датам. Кэширование можно применять, но оно не реализовано в этом
# курсе, чтобы можно было сравнить производительность между эндпоинтами.
async def get_rooms_by_time(
    hotel_id: int,
    date_from: date = Query(..., description=f"Например, {datetime.now().date()}"),  # Дата начала поиска
    date_to: date = Query(..., description=f"Например, {(datetime.now() + timedelta(days=14)).date()}"),  # Дата окончания поиска
) -> List[SRoomInfo]:  # Возвращает список информации о номерах
    rooms = await RoomDAO.find_all(hotel_id, date_from, date_to)  # Получение доступных номеров через DAO
    return rooms  # Возврат списка найденных номеров
