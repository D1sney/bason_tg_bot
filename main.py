import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN
from handlers.manager_handlers import manager_router
from handlers.warehouse_handlers import warehouse_router
from handlers.issuance_handler import issuing_router

# Настройка логирования для файла main.py
logger = logging.getLogger("main")
logger.setLevel(logging.INFO)

# Создаем обработчик для записи логов в файл
file_handler = logging.FileHandler("bot.log", mode="a")
file_handler.setLevel(logging.INFO)

# Создаем обработчик для вывода логов в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Формат лог-сообщений: время, имя логгера, уровень и само сообщение
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Добавляем обработчики к логгеру
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Создаем объекты бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Подключаем роутеры
dp.include_router(manager_router)
dp.include_router(warehouse_router)
dp.include_router(issuing_router)

# Функция для установки команд меню бота
async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Помощь"),
    ]
    await bot.set_my_commands(commands)

async def main():
    logger.info("Запуск бота...")
    await set_bot_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())