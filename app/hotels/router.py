from datetime import date, datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Query
from fastapi_cache.decorator import cache

from app.exceptions import CannotBookHotelForLongPeriod, DateFromCannotBeAfterDateTo
from app.hotels.dao import HotelDAO
from app.hotels.schemas import SHotel, SHotelInfo

router = APIRouter(prefix="/hotels", tags=["Отели"])  # Создание маршрутизатора для эндпоинтов отелей


@router.get("/{location}")
@cache(expire=30)  # Кэширование результата запроса на 30 секунд
async def get_hotels_by_location_and_time(
    location: str,
    date_from: date = Query(..., description=f"Например, {datetime.now().date()}"),
    date_to: date = Query(..., description=f"Например, {(datetime.now() + timedelta(days=14)).date()}"),
) -> List[SHotelInfo]:
    # Проверка, что дата начала не позже даты окончания
    if date_from > date_to:
        raise DateFromCannotBeAfterDateTo
    # Проверка, что период бронирования не превышает 31 день
    if (date_to - date_from).days > 31:
        raise CannotBookHotelForLongPeriod
    # Получение всех отелей по локации и датам
    hotels = await HotelDAO.find_all(location, date_from, date_to)
    return hotels


@router.get("/id/{hotel_id}", include_in_schema=True)
# Этот эндпоинт используется для фронтенда, чтобы отобразить информацию о номерах в отеле
# и информацию о самом отеле.
async def get_hotel_by_id(
    hotel_id: int,
) -> Optional[SHotel]:
    # Получение информации об отеле по его уникальному идентификатору
    return await HotelDAO.find_one_or_none(id=hotel_id)
