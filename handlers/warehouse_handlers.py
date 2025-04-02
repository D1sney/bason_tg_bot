import logging
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import ISSUANCE_CHAT_ID, MANAGER_CHAT_ID, LOST_CHAT_ID

# Создаем логгер для этого файла
logger = logging.getLogger("warehouse_handlers")
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

# Создаем роутер для складского чата
warehouse_router = Router()

# Инлайн-кнопки для выдачи
issuing_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Продано", callback_data="issued_sold"),
         InlineKeyboardButton(text="Возврат на склад", callback_data="issued_return")]
    ]
)

# Обработчик inline-кнопок в складском чате
@warehouse_router.callback_query(F.data.in_({"warehouse_yes", "warehouse_no"}))
async def warehouse_response(callback: CallbackQuery):
    logger.info("Получен callback с данными '%s' от пользователя id=%s", callback.data, callback.from_user.id)
    response = "Деталь есть" if callback.data == "warehouse_yes" else "Детали нет"
    logger.info("Исходный текст сообщения: %s", callback.message.text)
    await callback.message.edit_text(f"{callback.message.text}\nОтвет склада: {response}")
    
    if callback.data == "warehouse_yes":
        # Если действие "Вынести деталь", отправляем в чат выдачи
        if "Вынести деталь" in callback.message.text:
            issuing_chat_id = ISSUANCE_CHAT_ID  # ID чата выдачи
            logger.info("Пересылаем сообщение в чат выдачи (id=%s)", issuing_chat_id)
            await callback.bot.send_message(
                issuing_chat_id,
                callback.message.text + "\nПередано в чат выдачи.",
                reply_markup=issuing_keyboard
            )
        else:
            manager_chat_id = MANAGER_CHAT_ID  # ID чата менеджеров
            logger.info("Уведомляем менеджеров (id=%s) о наличии детали", manager_chat_id)
            await callback.bot.send_message(
                manager_chat_id,
                callback.message.text + "\nДеталь есть, наличие подтвеждено."
            )
    else:
        # Если детали нет, уведомляем менеджеров
        manager_chat_id = MANAGER_CHAT_ID  # ID чата менеджеров
        logger.info("Уведомляем менеджеров (id=%s) об отсутствии детали", manager_chat_id)
        await callback.bot.send_message(
            manager_chat_id,
            callback.message.text + "\nДетали нет, запрос отменен."
        )
        # Если детали нет, отправляем в группу потерянных деталей
        lost_chat_id = LOST_CHAT_ID  # ID чата потеряшек
        logger.info("Отправляем сообщение в чат потерянных деталей (id=%s)", lost_chat_id)
        await callback.bot.send_message(
            lost_chat_id,
            callback.message.text + "\nДобавлено в список потерянных деталей."
        )
    await callback.answer()
