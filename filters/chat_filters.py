from aiogram.filters import BaseFilter
from aiogram.types import Message
import os

# ID чатов из переменных окружения
MANAGER_CHAT_ID = int(os.getenv("MANAGER_CHAT_ID", 0))
WAREHOUSE_CHAT_ID = int(os.getenv("WAREHOUSE_CHAT_ID", 0))
ISSUANCE_CHAT_ID = int(os.getenv("ISSUANCE_CHAT_ID", 0))
FINAL_CHAT_ID = int(os.getenv("FINAL_CHAT_ID", 0))

class ManagerChatFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.chat.id == MANAGER_CHAT_ID

class WarehouseChatFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.chat.id == WAREHOUSE_CHAT_ID

class IssuanceChatFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.chat.id == ISSUANCE_CHAT_ID

class FinalChatFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.chat.id == FINAL_CHAT_ID