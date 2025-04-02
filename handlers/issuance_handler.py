import logging
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import SOLD_CHAT_ID, WAREHOUSE_CHAT_ID

# Создаем логгер для этого файла
logger = logging.getLogger("issuance_handlers")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    file_handler = logging.FileHandler("bot.log", mode="a")
    file_handler.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# Создаем роутер для чата с выдачей
issuing_router = Router()

# Обработчик inline-кнопок в чате выдачи
@issuing_router.callback_query(F.data.in_({"issued_sold", "issued_return"}))
async def issuing_response(callback: CallbackQuery):
    logger.info("Получен callback с данными '%s' от пользователя id=%s", callback.data, callback.from_user.id)
    response = "Деталь продана" if callback.data == "issued_sold" else "Деталь возвращена на склад"
    logger.info("Формируется ответ: %s", response)
    await callback.message.edit_text(f"{callback.message.text}\nОтвет выдачи: {response}")
    
    if callback.data == "issued_sold":
        sold_chat_id = SOLD_CHAT_ID  # ID чата с проданными деталями
        logger.info("Пересылаем сообщение в чат с проданными деталями (id=%s)", sold_chat_id)
        await callback.bot.send_message(
            sold_chat_id,
            callback.message.text + "\nДобавлено в список проданных деталей."
        )
    else:
        warehouse_chat_id = WAREHOUSE_CHAT_ID  # ID складского чата
        logger.info("Пересылаем сообщение в складской чат (id=%s)", warehouse_chat_id)
        await callback.bot.send_message(
            warehouse_chat_id,
            callback.message.text + "\nДеталь возвращена на склад."
        )
    await callback.answer()
