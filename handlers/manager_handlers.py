from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from filters.chat_filters import ManagerChatFilter
from services.api_service import send_to_warehouse_chat
from config import WAREHOUSE_CHAT_ID, MANAGER_CHAT_ID

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
        await send_to_warehouse_chat(message, WAREHOUSE_CHAT_ID, MANAGER_CHAT_ID, article, action, warehouse_keyboard)
    else:
        await message.answer("Артикул введен с ошибкой. Попробуйте снова.")

# Обработчик команды /start
@manager_router.message()
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(ManagerStates.choose_action)
    await message.answer("Выберите действие:", reply_markup=action_keyboard)
