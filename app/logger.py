import logging  # Импортируем модуль для ведения логов
from datetime import datetime  # Импортируем datetime для работы с датой и временем

from pythonjsonlogger import jsonlogger  # Импортируем jsonlogger для форматирования логов в формате JSON

from app.config import settings  # Импортируем настройки приложения

# Создаем экземпляр логгера
logger = logging.getLogger()

# Создаем обработчик для вывода логов в поток (консоль)
logHandler = logging.StreamHandler()


# Определяем класс для форматирования логов в формате JSON
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        # Вызываем метод родительского класса для добавления полей
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)

        # Добавляем временную метку, если она отсутствует
        if not log_record.get("timestamp"):
            now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")  # Получаем текущее время в UTC
            log_record["timestamp"] = now  # Добавляем временную метку в лог

        # Приводим уровень логирования к верхнему регистру
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()  # Приводим уровень к верхнему регистру
        else:
            log_record["level"] = record.levelname  # Если уровень не установлен, используем уровень из record


# Создаем экземпляр форматировщика, определяя поля для вывода в лог
formatter = CustomJsonFormatter(
    "%(timestamp)s %(level)s %(message)s %(module)s %(funcName)s"  # Определяем, какие поля будут выводиться
)

logHandler.setFormatter(formatter)  # Устанавливаем форматировщик для обработчика логов
logger.addHandler(logHandler)  # Добавляем обработчик в логгер
logger.setLevel(settings.LOG_LEVEL)  # Устанавливаем уровень логирования, основанный на настройках
