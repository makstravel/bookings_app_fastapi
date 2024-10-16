from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.bookings.router import add_booking, get_bookings
from app.hotels.rooms.router import get_rooms_by_time
from app.hotels.router import get_hotel_by_id, get_hotels_by_location_and_time
from app.utils import format_number_thousand_separator, get_month_days

# Создание экземпляра APIRouter для управления маршрутами фронтенда
router = APIRouter(
    prefix="/pages",  # Префикс для всех маршрутов в этом роутере
    tags=["Фронтенд"]  # Тэги для группировки маршрутов в документации
)

# Инициализация Jinja2 для рендеринга шаблонов из директории "app/templates"
templates = Jinja2Templates(directory="app/templates")

# Эндпоинт для получения страницы логина
@router.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

# Эндпоинт для получения страницы регистрации
@router.get("/register", response_class=HTMLResponse)
async def get_register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

# Эндпоинт для получения страницы с отелями по локации
@router.get("/hotels/{location}", response_class=HTMLResponse)
async def get_hotels_page(
    request: Request,
    location: str,
    date_to: date,
    date_from: date,
    hotels=Depends(get_hotels_by_location_and_time),  # Зависимость для получения отелей
):
    dates = get_month_days()  # Получаем дни месяца для отображения
    if date_from > date_to:  # Проверяем, чтобы дата заезда не была позже даты выезда
        date_to, date_from = date_from, date_to
    # Автоматически ставим дату заезда позже текущей даты
    date_from = max(datetime.today().date(), date_from)
    # Автоматически ставим дату выезда не позже, чем через 180 дней
    date_to = min((datetime.today() + timedelta(days=180)).date(), date_to)
    return templates.TemplateResponse(
        "hotels_and_rooms/hotels.html",  # Шаблон для страницы отелей
        {
            "request": request,
            "hotels": hotels,
            "location": location,
            "date_to": date_to.strftime("%Y-%m-%d"),  # Форматируем даты для отображения
            "date_from": date_from.strftime("%Y-%m-%d"),
            "dates": dates,
        },
    )

# Эндпоинт для получения страницы с номерами отеля
@router.get("/hotels/{hotel_id}/rooms", response_class=HTMLResponse)
async def get_rooms_page(
    request: Request,
    date_from: date,
    date_to: date,
    rooms=Depends(get_rooms_by_time),  # Зависимость для получения номеров
    hotel=Depends(get_hotel_by_id),  # Зависимость для получения информации об отеле
):
    date_from_formatted = date_from.strftime("%d.%m.%Y")  # Форматируем дату заезда
    date_to_formatted = date_to.strftime("%d.%m.%Y")  # Форматируем дату выезда
    booking_length = (date_to - date_from).days  # Вычисляем длину бронирования
    return templates.TemplateResponse(
        "hotels_and_rooms/rooms.html",  # Шаблон для страницы номеров
        {
            "request": request,
            "hotel": hotel,
            "rooms": rooms,
            "date_from": date_from,
            "date_to": date_to,
            "booking_length": booking_length,
            "date_from_formatted": date_from_formatted,
            "date_to_formatted": date_to_formatted,
        },
    )

# Эндпоинт для получения страницы успешного бронирования
@router.post("/successful_booking", response_class=HTMLResponse)
async def get_successful_booking_page(
    request: Request,
    _=Depends(add_booking),  # Зависимость для добавления бронирования
):
    return templates.TemplateResponse(
        "bookings/booking_successful.html",  # Шаблон для страницы успешного бронирования
        {"request": request}
    )

# Эндпоинт для получения страницы со списком бронирований
@router.get("/bookings", response_class=HTMLResponse)
async def get_bookings_page(
    request: Request,
    bookings=Depends(get_bookings),  # Зависимость для получения списка бронирований
):
    return templates.TemplateResponse(
        "bookings/bookings.html",  # Шаблон для страницы бронирований
        {
            "request": request,
            "bookings": bookings,
            "format_number_thousand_separator": format_number_thousand_separator,  # Форматирование чисел
        },
    )
