import logging
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from filters.chat_filters import ManagerChatFilter
from services.api_service import send_to_warehouse_chat
from config import WAREHOUSE_CHAT_ID, MANAGER_CHAT_ID

# Создаем логгер для этого файла
logger = logging.getLogger("manager_handlers")
logger.setLevel(logging.INFO)
if not logger.hasHandlers():
    # Обработчик для записи логов в файл
    file_handler = logging.FileHandler("bot.log", mode="a")
    file_handler.setLevel(logging.INFO)
    # Обработчик для вывода логов в консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

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
    logger.info("Команда /start от пользователя id=%s, username=%s", message.from_user.id, message.from_user.username)
    await state.set_state(ManagerStates.choose_action)
    await message.answer("Выберите действие:", reply_markup=action_keyboard)

# Обработчик выбора действия
@manager_router.message(ManagerStates.choose_action, F.text.in_({"Проверить наличие", "Вынести деталь"}))
async def choose_action(message: Message, state: FSMContext):
    logger.info("Пользователь id=%s выбрал действие: %s", message.from_user.id, message.text)
    await state.update_data(action=message.text)
    await state.set_state(ManagerStates.enter_article)
    await message.answer("Укажите артикул детали:", reply_markup=cancel_keyboard)

# Обработчик кнопки отмены
@manager_router.message(ManagerStates.enter_article, F.text == "Отменить ввод артикула")
async def cancel_article_input(message: Message, state: FSMContext):
    logger.info("Пользователь id=%s отменил ввод артикула", message.from_user.id)
    await state.clear()
    await state.set_state(ManagerStates.choose_action)
    await message.answer("Ввод артикула отменен.", reply_markup=action_keyboard)

# Обработчик ввода артикула
@manager_router.message(ManagerStates.enter_article)
async def enter_article(message: Message, state: FSMContext):
    article = message.text.strip()
    logger.info("Пользователь id=%s ввел артикул: %s", message.from_user.id, article)
    # TODO: добавить проверку по регулярному выражению
    if True:  # Здесь будет проверка артикула
        data = await state.get_data()
        action = data.get("action", "Неизвестно")
        await state.clear()
        await state.set_state(ManagerStates.choose_action)
        await message.answer(f"Ваш запрос: {action} для артикула {article}. Отправляем данные...")
        await message.answer("Выберите действие:", reply_markup=action_keyboard)
        logger.info("Отправка данных для артикула %s, действие: %s", article, action)
        # Отправка сообщения в складской чат
        await send_to_warehouse_chat(message, WAREHOUSE_CHAT_ID, MANAGER_CHAT_ID, article, action, warehouse_keyboard)
    else:
        logger.warning("Пользователь id=%s ввел неверный артикул: %s", message.from_user.id, article)
        await message.answer("Артикул введен с ошибкой. Попробуйте снова.")

# Обработчик для остальных сообщений (fallback)
@manager_router.message()
async def fallback_handler(message: Message, state: FSMContext):
    logger.info("Fallback handler: получено сообщение от пользователя id=%s с текстом: %s", message.from_user.id, message.text)
    await state.set_state(ManagerStates.choose_action)
    await message.answer("Выберите действие:", reply_markup=action_keyboard)
