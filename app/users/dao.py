from app.dao.base import BaseDAO
from app.users.models import Users

class UserDAO(BaseDAO):
    """
    Data Access Object для работы с моделью Users.
    """
    model = Users
