from fastapi import APIRouter, Depends, Response

from app.exceptions import (
    CannotAddDataToDatabase,  # Исключение, если не удалось добавить данные в БД
    UserAlreadyExistsException,  # Исключение, если пользователь уже существует
)
from app.users.auth import authenticate_user, create_access_token, get_password_hash  # Импорт функций для аутентификации
from app.users.dao import UserDAO  # Импорт DAO для работы с пользователями
from app.users.dependencies import get_current_user  # Импорт зависимости для получения текущего пользователя
from app.users.models import Users  # Импорт модели пользователя
from app.users.schemas import SUserAuth  # Импорт схемы для аутентификации пользователя

# Создание маршрутизатора для аутентификации
router_auth = APIRouter(
    prefix="/auth",  # Префикс для маршрутов аутентификации
    tags=["Auth"],  # Метка для документации
)

# Создание маршрутизатора для пользователей
router_users = APIRouter(
    prefix="/users",  # Префикс для маршрутов пользователей
    tags=["Пользователи"],  # Метка для документации
)

@router_auth.post("/register", status_code=201)  # Определение маршрута для регистрации пользователя
async def register_user(user_data: SUserAuth):  # Ожидает данные пользователя согласно схеме SUserAuth
    # Проверяем, существует ли пользователь с указанным email
    existing_user = await UserDAO.find_one_or_none(email=user_data.email)
    if existing_user:  # Если пользователь найден
        raise UserAlreadyExistsException  # Выбрасываем исключение

    # Хешируем пароль пользователя перед сохранением
    hashed_password = get_password_hash(user_data.password)
    # Сохраняем нового пользователя в базе данных
    new_user = await UserDAO.add(email=user_data.email, hashed_password=hashed_password)
    if not new_user:  # Если не удалось добавить пользователя
        raise CannotAddDataToDatabase  # Выбрасываем исключение

@router_auth.post("/login")  # Определение маршрута для входа пользователя
async def login_user(response: Response, user_data: SUserAuth):  # Ожидает данные пользователя согласно схеме SUserAuth
    # Аутентифицируем пользователя с помощью email и пароля
    user = await authenticate_user(user_data.email, user_data.password)
    # Создаем токен доступа для пользователя
    access_token = create_access_token({"sub": str(user.id)})
    # Устанавливаем cookie с токеном доступа, чтобы клиент мог его использовать
    response.set_cookie("booking_access_token", access_token, httponly=True)
    return {"access_token": access_token}  # Возвращаем токен доступа

@router_auth.post("/logout")  # Определение маршрута для выхода пользователя
async def logout_user(response: Response):  # Удаляет cookie с токеном доступа
    response.delete_cookie("booking_access_token")  # Удаляем cookie с токеном доступа

@router_users.get("/me")  # Определение маршрута для получения информации о текущем пользователе
async def read_users_me(current_user: Users = Depends(get_current_user)):  # Получаем текущего пользователя
    return current_user  # Возвращаем информацию о текущем пользователе
