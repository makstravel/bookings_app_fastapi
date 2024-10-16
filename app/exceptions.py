from fastapi import HTTPException, status  # Импортируем класс HTTPException и статусы HTTP из FastAPI


# Создание собственных исключений (exceptions) было изменено
# на предпочтительный подход.
# Подробнее в курсе: https://stepik.org/lesson/919993/step/15?unit=925776

# Базовый класс для всех исключений, связанных с бронированием
class BookingException(HTTPException):
    status_code = 500  # Код состояния по умолчанию для ошибки сервера
    detail = ""  # Подробности об ошибке (по умолчанию пустые)

    def __init__(self):
        # Инициализация базового класса с заданным кодом состояния и деталями
        super().__init__(status_code=self.status_code, detail=self.detail)


# Исключение для случая, когда пользователь уже существует
class UserAlreadyExistsException(BookingException):
    status_code = status.HTTP_409_CONFLICT  # Код состояния 409: конфликт
    detail = "Пользователь уже существует"  # Подробности об ошибке


# Исключение для неверной электронной почты или пароля
class IncorrectEmailOrPasswordException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED  # Код состояния 401: неавторизован
    detail = "Неверная почта или пароль"  # Подробности об ошибке


# Исключение для истекшего токена
class TokenExpiredException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED  # Код состояния 401: неавторизован
    detail = "Срок действия токена истек"  # Подробности об ошибке


# Исключение для отсутствующего токена
class TokenAbsentException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED  # Код состояния 401: неавторизован
    detail = "Токен отсутствует"  # Подробности об ошибке


# Исключение для неверного формата токена
class IncorrectTokenFormatException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED  # Код состояния 401: неавторизован
    detail = "Неверный формат токена"  # Подробности об ошибке


# Исключение для случая, когда пользователь не найден
class UserIsNotPresentException(BookingException):
    status_code = status.HTTP_401_UNAUTHORIZED  # Код состояния 401: неавторизован


# Исключение для полностью забронированной комнаты
class RoomFullyBooked(BookingException):
    status_code = status.HTTP_409_CONFLICT  # Код состояния 409: конфликт
    detail = "Не осталось свободных номеров"  # Подробности об ошибке


# Исключение для ситуации, когда невозможно забронировать номер
class RoomCannotBeBooked(BookingException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR  # Код состояния 500: ошибка сервера
    detail = "Не удалось забронировать номер ввиду неизвестной ошибки"  # Подробности об ошибке


# Исключение для случаев, когда дата заезда позже даты выезда
class DateFromCannotBeAfterDateTo(BookingException):
    status_code = status.HTTP_400_BAD_REQUEST  # Код состояния 400: неверный запрос
    detail = "Дата заезда не может быть позже даты выезда"  # Подробности об ошибке


# Исключение для бронирования отеля на слишком длительный срок
class CannotBookHotelForLongPeriod(BookingException):
    status_code = status.HTTP_400_BAD_REQUEST  # Код состояния 400: неверный запрос
    detail = "Невозможно забронировать отель сроком более месяца"  # Подробности об ошибке


# Исключение для случаев, когда не удалось добавить запись в базу данных
class CannotAddDataToDatabase(BookingException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR  # Код состояния 500: ошибка сервера
    detail = "Не удалось добавить запись"  # Подробности об ошибке


# Исключение для обработки CSV файла
class CannotProcessCSV(BookingException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR  # Код состояния 500: ошибка сервера
    detail = "Не удалось обработать CSV файл"  # Подробности об ошибке
