from typing import List, Optional

from pydantic import BaseModel


class SRoom(BaseModel):
    # Модель для представления информации о номере
    id: int  # Уникальный идентификатор номера
    hotel_id: int  # Идентификатор отеля, к которому принадлежит номер
    name: str  # Название номера
    description: Optional[str]  # Описание номера (может быть пустым)
    services: List[str]  # Список услуг, предоставляемых с номером
    price: int  # Цена номера за ночь
    quantity: int  # Количество доступных номеров
    image_id: int  # Идентификатор изображения номера

    class Config:
        orm_mode = True  # Включает работу с ORM, позволяя преобразовывать объекты SQLAlchemy в Pydantic модели


class SRoomInfo(SRoom):
    # Модель для представления информации о номере с дополнительными полями
    total_cost: int  # Общая стоимость бронирования
    rooms_left: int  # Количество оставшихся доступных номеров

    class Config:
        orm_mode = True  # Включает работу с ORM
