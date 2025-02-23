from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from filters.chat_filters import ManagerChatFilter
from services.api_service import get_item_info
from config import WAREHOUSE_CHAT_ID

# Создаем роутер
manager_router = Router()
manager_router.message.filter(ManagerChatFilter())

# Определяем состояния
class ManagerStates(StatesGroup):
    choose_action = State()
    enter_article = State()

# Клавиатуры
action_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Проверить наличие"), KeyboardButton(text="Вынести деталь")]],
    resize_keyboard=True
)

cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Отменить ввод артикула")]],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Инлайн-кнопки для складского чата
warehouse_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Есть", callback_data="warehouse_yes"),
         InlineKeyboardButton(text="Нет", callback_data="warehouse_no")]
    ]
)

# Обработчик команды /start
@manager_router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(ManagerStates.choose_action)
    await message.answer("Выберите действие:", reply_markup=action_keyboard)

# Обработчик выбора действия
@manager_router.message(ManagerStates.choose_action, F.text.in_({"Проверить наличие", "Вынести деталь"}))
async def choose_action(message: Message, state: FSMContext):
    await state.update_data(action=message.text)
    await state.set_state(ManagerStates.enter_article)
    await message.answer("Укажите артикул детали:", reply_markup=cancel_keyboard)

# Обработчик кнопки отмены
@manager_router.message(ManagerStates.enter_article, F.text == "Отменить ввод артикула")
async def cancel_article_input(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(ManagerStates.choose_action)
    await message.answer("Ввод артикула отменен.", reply_markup=action_keyboard)


# Отправка сообщения в складской чат
async def send_to_warehouse_chat(message, warehouse_chat_id: int, item_id: int, action: str):
    """Отправляет информацию о товаре в складской чат."""
    # item_info = get_item_info(item_id)
    # if item_info:
    #     message_text = (f"Запрос: {action}\n"
    #                     f"Артикул: {item_info['article']}\n"
    #                     f"Секция: {item_info['section']}")
    #     await message.bot.send_photo(warehouse_chat_id, item_info['photo_url'], caption=message_text)
    # else:
    #     await message.bot.send_message(warehouse_chat_id, "Ошибка: не удалось получить информацию о товаре.")
    """Временное решение пока не понятки с API"""
    await message.bot.send_message(warehouse_chat_id, f'Запрос: {action}\nАртикул: {item_id}\n', reply_markup=warehouse_keyboard)

# Обработчик ввода артикула
@manager_router.message(ManagerStates.enter_article)
async def enter_article(message: Message, state: FSMContext):
    article = message.text.strip()
    # TODO: добавить проверку по регулярному выражению
    if True:  # Здесь будет проверка артикула
        data = await state.get_data()
        action = data.get("action", "Неизвестно")
        await state.clear()
        await state.set_state(ManagerStates.choose_action)
        await message.answer(f"Ваш запрос: {action} для артикула {article}. Отправляем данные...")
        await message.answer("Выберите действие:", reply_markup=action_keyboard)
        # Отправка сообщения в складской чат
        await send_to_warehouse_chat(message, WAREHOUSE_CHAT_ID, article, action)
    else:
        await message.answer("Артикул введен с ошибкой. Попробуйте снова.")
