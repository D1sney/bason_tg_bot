from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

# Создаем роутер для складского чата
warehouse_router = Router()

# Инлайн-кнопки для складского чата
warehouse_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Есть", callback_data="warehouse_yes"),
         InlineKeyboardButton(text="Нет", callback_data="warehouse_no")]
    ]
)

# Обработчик inline-кнопок в складском чате
@warehouse_router.callback_query(F.data.in_({"warehouse_yes", "warehouse_no"}))
async def warehouse_response(callback: CallbackQuery):
    response = "Деталь есть" if callback.data == "warehouse_yes" else "Детали нет"
    await callback.message.edit_text(f"{callback.message.text}\nОтвет склада: {response}")
    
    if callback.data == "warehouse_yes":
        # Если действие "Вынести деталь", отправляем в чат выдачи
        if "Вынести деталь" in callback.message.text:
            issuing_chat_id = -1009876543210  # Условный ID чата выдачи
            await callback.bot.send_message(
                issuing_chat_id,
                callback.message.text + "\nПередано в чат выдачи."
            )
    else:
        # Если детали нет, уведомляем менеджеров
        manager_chat_id = -1001122334455  # Условный ID чата менеджеров
        await callback.bot.send_message(
            manager_chat_id,
            callback.message.text + "\nДетали нет, запрос отменен."
        )
    await callback.answer()