import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from filters.chat_filters import ManagerChatFilter
from handlers.manager_handlers import manager_router
from handlers.warehouse_handlers import warehouse_router
from handlers.issuance_handler import issuing_router
# Загружаем переменные окружения
from config import TOKEN


# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Создаём объекты бота и диспетчера
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
    logging.info("Запуск бота...")
    await set_bot_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())