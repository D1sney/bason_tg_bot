from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from config import SOLD_CHAT_ID, WAREHOUSE_CHAT_ID


# Создаем роутер для чата с выдачей
issuing_router = Router()


# Обработчик inline-кнопок в чате выдачи
@issuing_router.callback_query(F.data.in_({"issued_sold", "issued_return"}))
async def issuing_response(callback: CallbackQuery):
    response = "Деталь продана" if callback.data == "issued_sold" else "Деталь возвращена на склад"
    await callback.message.edit_text(f"{callback.message.text}\nОтвет выдачи: {response}")
    
    if callback.data == "issued_sold":
        # Отправляем в чат с проданными деталями
        sold_chat_id = SOLD_CHAT_ID  # Условный ID чата с проданными деталями
        await callback.bot.send_message(
            sold_chat_id,
            callback.message.text + "\nДобавлено в список проданных деталей."
        )
    else:
        # Отправляем обратно в складской чат
        warehouse_chat_id = WAREHOUSE_CHAT_ID  # Условный ID складского чата
        await callback.bot.send_message(
            warehouse_chat_id,
            callback.message.text + "\nДеталь возвращена на склад."
        )
    await callback.answer()
