from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from filters.chat_filters import ManagerChatFilter

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

# Обработчик ввода артикула
@manager_router.message(ManagerStates.enter_article)
async def enter_article(message: Message, state: FSMContext):
    article = message.text.strip()
    # TODO: добавить проверку по регулярному выражению
    if True:  # Здесь будет проверка артикула
        data = await state.get_data()
        action = data.get("action", "Неизвестно")
        await state.clear()
        await message.answer(f"Ваш запрос: {action} для артикула {article}. Отправляем данные...")
    else:
        await message.answer("Артикул введен с ошибкой. Попробуйте снова.")

# Обработчик кнопки отмены
@manager_router.message(ManagerStates.enter_article, F.text == "Отменить ввод артикула")
async def cancel_article_input(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Ввод артикула отменен.", reply_markup=action_keyboard)