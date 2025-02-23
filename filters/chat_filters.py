from aiogram.filters import BaseFilter
from aiogram.types import Message
import os
# ID чатов из переменных окружения
from config import MANAGER_CHAT_ID, WAREHOUSE_CHAT_ID, ISSUANCE_CHAT_ID, SOLD_CHAT_ID


class ManagerChatFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.chat.id == int(MANAGER_CHAT_ID)

class WarehouseChatFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.chat.id == int(WAREHOUSE_CHAT_ID)

class IssuanceChatFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.chat.id == int(ISSUANCE_CHAT_ID)

class SoldChatFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.chat.id == int(SOLD_CHAT_ID)