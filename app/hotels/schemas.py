from typing import List
from pydantic import BaseModel

class SHotel(BaseModel):
    id: int  # Уникальный идентификатор отеля
    name: str  # Название отеля
    location: str  # Местоположение отеля
    services: List[str]  # Список услуг, предлагаемых отелем
    rooms_quantity: int  # Общее количество номеров в отеле
    image_id: int  # Идентификатор изображения отеля

    class Config:
        orm_mode = True  # Включение режима совместимости с ORM для Pydantic


class SHotelInfo(SHotel):
    rooms_left: int  # Количество свободных номеров в отеле

    class Config:
        orm_mode = True  # Включение режима совместимости с ORM для Pydantic
