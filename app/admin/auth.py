from typing import Optional
from app.logger import logger  # Логгер для записи сообщений отладки
from sqladmin.authentication import AuthenticationBackend  # Базовый класс для аутентификации SQLAdmin
from starlette.requests import Request  # Модуль для обработки HTTP запросов
from starlette.responses import RedirectResponse  # Модуль для отправки перенаправлений в ответ на запрос

from app.users.auth import authenticate_user, \
    create_access_token  # Функции для аутентификации пользователя и создания токена доступа
from app.users.dependencies import get_current_user  # Зависимость для получения текущего пользователя


class AdminAuth(AuthenticationBackend):
    """
    Класс для управления аутентификацией администратора.
    Реализует методы логина, логаута и аутентификации пользователя через токен.
    """

    async def login(self, request: Request) -> bool:
        """
        Метод для входа в систему.
        Получает данные формы (email и пароль), аутентифицирует пользователя,
        создает токен доступа и сохраняет его в сессии запроса.

        :param request: объект запроса от клиента
        :return: True, если процесс завершен
        """
        form = await request.form()  # Получаем данные из формы запроса
        email, password = form["username"], form["password"]  # Извлекаем email и пароль из формы

        # Проверяем пользователя по email и паролю
        user = await authenticate_user(email, password)
        if user:
            # Если пользователь аутентифицирован, создаем токен доступа
            access_token = create_access_token({"sub": str(user.id)})
            request.session.update({"token": access_token})  # Сохраняем токен в сессии

        return True

    async def logout(self, request: Request) -> bool:
        """
        Метод для выхода из системы.
        Очищает сессию пользователя.

        :param request: объект запроса от клиента
        :return: True, если процесс завершен
        """
        request.session.clear()  # Очищаем сессию, чтобы завершить сессию пользователя
        return True

    async def authenticate(self, request: Request) -> Optional[RedirectResponse]:
        """
        Метод для аутентификации пользователя.
        Проверяет наличие токена в сессии запроса и, если его нет или он недействителен,
        перенаправляет на страницу входа.

        :param request: объект запроса от клиента
        :return: Ответ с перенаправлением на страницу входа или None, если аутентификация успешна
        """
        token = request.session.get("token")  # Извлекаем токен из сессии

        if not token:
            # Если токен отсутствует, перенаправляем на страницу входа
            return RedirectResponse(request.url_for("admin:login"), status_code=302)

        # Проверяем действительность токена и получаем текущего пользователя
        user = await get_current_user(token)
        logger.debug(f"{user=}")  # Логируем информацию о пользователе для отладки
        if not user:
            # Если пользователь не найден, перенаправляем на страницу входа
            return RedirectResponse(request.url_for("admin:login"), status_code=302)


# Экземпляр класса аутентификации администратора с секретным ключом
authentication_backend = AdminAuth(secret_key="...")
