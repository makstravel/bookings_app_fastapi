import shutil
from fastapi import APIRouter, UploadFile
from app.tasks.tasks import process_pic

# Создание экземпляра маршрутизатора FastAPI с префиксом "/images" и тегом "Загрузка картинок"
router = APIRouter(
    prefix="/images",
    tags=["Загрузка картинок"]
)


@router.post("/hotels")
async def add_hotel_image(name: int, file: UploadFile):
    # Формируем путь для сохранения изображения, используя переданное имя (id) отеля
    im_path = f"app/static/images/{name}.webp"

    # Открываем файл для записи в бинарном режиме
    with open(im_path, "wb+") as file_object:
        # Сохраняем загруженный файл в локальное хранилище (обычно используется удаленное хранилище в реальных приложениях)
        shutil.copyfileobj(file.file, file_object)

    # Отправляем задачу на обработку изображения в фоновый режим с использованием Celery
    process_pic.delay(im_path)
