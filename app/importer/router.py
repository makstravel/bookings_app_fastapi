import codecs
import csv
from typing import Literal

from fastapi import APIRouter, Depends, UploadFile

from app.exceptions import CannotAddDataToDatabase, CannotProcessCSV
from app.importer.utils import TABLE_MODEL_MAP, convert_csv_to_postgres_format
from app.users.dependencies import get_current_user

# Создание экземпляра маршрутизатора FastAPI с префиксом "/import" и тегом "Импорт данных в БД"
router = APIRouter(
    prefix="/import",
    tags=["Импорт данных в БД"],
)


@router.post(
    "/{table_name}",
    status_code=201,  # Установить статус ответа на 201 (Создано)
    dependencies=[Depends(get_current_user)],  # Зависимость для проверки текущего пользователя
)
async def import_data_to_table(
        file: UploadFile,  # Файл, который будет загружен
        table_name: Literal["hotels", "rooms", "bookings"],  # Название таблицы для импорта данных
):
    ModelDAO = TABLE_MODEL_MAP[table_name]  # Получение соответствующего DAO для указанной таблицы

    # Декодирование загружаемого CSV файла и создание словаря для чтения данных
    # Внутри переменной file хранятся атрибуты:
    # file - сам файл, filename - название файла, size - размер файла.
    csvReader = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'), delimiter=";")

    # Преобразование данных из формата CSV в формат, подходящий для PostgreSQL
    data = convert_csv_to_postgres_format(csvReader)

    # Закрытие файла после чтения
    file.file.close()

    if not data:
        raise CannotProcessCSV  # Исключение, если данные не были обработаны

    # Пакетное добавление данных в базу данных через DAO
    added_data = await ModelDAO.add_bulk(data)

    if not added_data:
        raise CannotAddDataToDatabase  # Исключение, если добавление данных в БД не удалось
