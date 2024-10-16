# Импортируем ModelView из библиотеки sqladmin для создания интерфейсов администрирования моделей.
from sqladmin import ModelView

# Импортируем модели для работы с таблицами бронирования, отелей, номеров и пользователей.
from app.bookings.models import Bookings
from app.hotels.models import Hotels
from app.hotels.rooms.models import Rooms
from app.users.models import Users


# Класс для администрирования модели пользователей.
class UsersAdmin(ModelView, model=Users):
    # Определяем список колонок, которые будут отображаться в интерфейсе администратора.
    column_list = [Users.id, Users.email, Users.booking]

    # Исключаем из отображения колонку с хешированным паролем, чтобы не показывать ее в деталях.
    column_details_exclude_list = [Users.hashed_password]

    # Отключаем возможность удаления пользователей через интерфейс администратора.
    can_delete = False

    # Название модели в единственном числе для интерфейса.
    name = "Пользователь"

    # Название модели во множественном числе для интерфейса.
    name_plural = "Пользователи"

    # Иконка для интерфейса пользователя (используется Font Awesome).
    icon = "fa-solid fa-user"


# Класс для администрирования модели отелей.
class HotelsAdmin(ModelView, model=Hotels):
    # Определяем список колонок для отображения в интерфейсе.
    # Получаем все колонки таблицы Hotels через атрибут __table__.c и добавляем связанную модель Rooms.
    column_list = [c.name for c in Hotels.__table__.c] + [Hotels.rooms]

    # Название модели в единственном числе.
    name = "Отель"

    # Название модели во множественном числе.
    name_plural = "Отели"

    # Иконка для отображения отелей.
    icon = "fa-solid fa-hotel"


# Класс для администрирования модели номеров.
class RoomsAdmin(ModelView, model=Rooms):
    # Определяем список колонок для отображения.
    # Получаем все колонки таблицы Rooms и добавляем связанные модели Hotels и Bookings.
    column_list = [c.name for c in Rooms.__table__.c] + [Rooms.hotel, Rooms.booking]

    # Название модели в единственном числе.
    name = "Номер"

    # Название модели во множественном числе.
    name_plural = "Номера"

    # Иконка для отображения номеров.
    icon = "fa-solid fa-bed"


# Класс для администрирования модели бронирований.
class BookingsAdmin(ModelView, model=Bookings):
    # Определяем список колонок для отображения.
    # Получаем все колонки таблицы Bookings и добавляем связанные модели Users и Rooms.
    column_list = [c.name for c in Bookings.__table__.c] + [Bookings.user, Bookings.room]

    # Название модели в единственном числе.
    name = "Бронь"

    # Название модели во множественном числе.
    name_plural = "Брони"

    # Иконка для отображения бронирований.
    icon = "fa-solid fa-book"
