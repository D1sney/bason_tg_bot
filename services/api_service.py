import aiohttp
import os
from dotenv import load_dotenv
import asyncio

# Загружаем переменные окружения
load_dotenv()
API_URL = os.getenv("API_URL")
API_KEY = os.getenv("API_KEY")

async def fetch_item_details(article: str):
    """Запрашивает данные о товаре по артикулу из API."""
    url = f"{API_URL}/getProductsWithChars"
    params = {
        "order": "desc",
        "id": article
    }
    # headers = {
    #     "Authorization": f"Bearer {API_KEY}" if API_KEY else None
    # }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                return {"error": f"Ошибка API: {response.status}", "details": await response.text()}


async def get_item_info(article: str):
    """Получает информацию о товаре и извлекает нужные данные."""
    data = await fetch_item_details(article)
    if data:
        return {
            "photo_url": data.get("photo_url"),
            "article": data.get("article"),
            "section": data.get("section"),
        }
    return None


async def send_to_warehouse_chat(bot, warehouse_chat_id: int, item_info: dict, action: str):
    """Отправляет информацию о товаре в складской чат."""
    if item_info:
        message_text = (f"Запрос: {action}\n"
                        f"Артикул: {item_info['article']}\n"
                        f"Секция: {item_info['section']}")
        await bot.send_photo(warehouse_chat_id, item_info['photo_url'], caption=message_text)
    else:
        await bot.send_message(warehouse_chat_id, "Ошибка: не удалось получить информацию о товаре.")


print(asyncio.run(fetch_item_details(1)))