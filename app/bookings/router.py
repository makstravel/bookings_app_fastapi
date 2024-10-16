# Импортируем необходимые модули и зависимости для работы с API маршрутизацией, фоновыми задачами и зависимостями.
from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import parse_obj_as

# Импортируем DAO для взаимодействия с таблицей бронирований и схемы для обработки данных.
from app.bookings.dao import BookingDAO
from app.bookings.schemas import SBookingInfo, SNewBooking
# Импортируем собственные исключения и задачи для обработки событий.
from app.exceptions import RoomCannotBeBooked
from app.tasks.tasks import send_booking_confirmation_email
# Импортируем зависимости для получения текущего пользователя.
from app.users.dependencies import get_current_user
from app.users.models import Users

# Создаем экземпляр маршрутизатора с префиксом "/bookings" и меткой "Бронирования".
router = APIRouter(
    prefix="/bookings",
    tags=["Бронирования"],
)


# Маршрут для получения всех бронирований текущего пользователя.
@router.get("")
async def get_bookings(user: Users = Depends(get_current_user)) -> list[SBookingInfo]:
    # Используем DAO для получения всех бронирований с информацией о номере пользователя.
    return await BookingDAO.find_all_with_images(user_id=user.id)


# Маршрут для добавления нового бронирования.
@router.post("", status_code=201)
async def add_booking(
        booking: SNewBooking,  # Схема нового бронирования (данные, которые принимает запрос).
        background_tasks: BackgroundTasks,  # Фоновые задачи для выполнения после создания бронирования.
        user: Users = Depends(get_current_user),  # Получаем текущего пользователя через зависимость.
):
    # Используем DAO для добавления бронирования с указанными параметрами.
    booking = await BookingDAO.add(
        user.id,
        booking.room_id,
        booking.date_from,
        booking.date_to,
    )
    # Если бронирование не было создано, выбрасываем исключение.
    if not booking:
        raise RoomCannotBeBooked
    # Преобразуем объект бронирования в схему и возвращаем его в виде словаря.
    booking = parse_obj_as(SNewBooking, booking).dict()

    # Добавляем задачу отправки подтверждения бронирования по email.
    # Отправка через Celery (если используется), здесь закомментировано для примера.
    # send_booking_confirmation_email.delay(booking, user.email)

    # Используем встроенные фоновые задачи FastAPI.
    background_tasks.add_task(send_booking_confirmation_email, booking, user.email)
    return booking  # Возвращаем результат.


# Маршрут для удаления бронирования по его идентификатору.
@router.delete("/{booking_id}")
async def remove_booking(
        booking_id: int,  # Идентификатор бронирования, которое нужно удалить.
        current_user: Users = Depends(get_current_user),  # Получаем текущего пользователя через зависимость.
):
    # Используем DAO для удаления бронирования с указанным ID и проверкой на пользователя.
    await BookingDAO.delete(id=booking_id, user_id=current_user.id)
