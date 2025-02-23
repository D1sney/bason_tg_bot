import aiohttp
import os
import json
import asyncio
from config import API_URL, AUTH_API_URL, LOGIN_DATA

access_token = None
refresh_token = None

TOKENS_FILE = 'tokens.json'

def save_tokens(access_token, refresh_token):
    """Сохраняет AccessToken и RefreshToken в файл."""
    tokens = {
        "access_token": access_token,
        "refresh_token": refresh_token
    }
    with open(TOKENS_FILE, 'w') as file:
        json.dump(tokens, file)

def load_tokens():
    """Загружает AccessToken и RefreshToken из файла, если они есть."""
    global access_token, refresh_token
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, 'r') as file:
            tokens = json.load(file)
            access_token = tokens.get("access_token")
            refresh_token = tokens.get("refresh_token")

async def authenticate():
    """Функция для получения AccessToken и RefreshToken через логин"""
    global access_token, refresh_token
    # Сначала пытаемся загрузить токены из файла
    load_tokens()

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{AUTH_API_URL}/login/user", json=LOGIN_DATA) as response:
            data = await response.json()
            if data.get("success"):
                access_token = data["AT"]
                refresh_token = data["RT"]
                save_tokens(access_token, refresh_token)  # Сохраняем токены в файл
            elif data.get("error") == "need_captcha":
                # raise Exception("Ошибка аутентификации: требуется пройти капчу")
                print(data)
            else:
                raise Exception(f"Ошибка аутентификации: {data.get('error')}")

async def refresh_tokens():
    """Функция для обновления токенов через RefreshToken"""
    global access_token, refresh_token
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{AUTH_API_URL}/refresh/user", json={"RT": refresh_token}) as response:
            data = await response.json()
            if data.get("success"):
                access_token = data["AT"]
                refresh_token = data["RT"]
                save_tokens(access_token, refresh_token)  # Сохраняем обновленные токены в файл
            else:
                raise Exception("Ошибка обновления токена. Требуется повторная аутентификация.")

async def revoke_tokens():
    """Функция для отзыва токена"""
    global access_token, refresh_token
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{AUTH_API_URL}/revoke/user", json={"RT": refresh_token}) as response:
            data = await response.json()
            print(data)

async def fetch_item_details(item_id: int):
    """Запрашивает данные о товаре по артикулу из API."""
    global access_token
    url = f"{API_URL}/getProducts"
    params = {
        "order": "desc",
        "id": item_id
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 401:  # Если AccessToken истек, обновляем
                await refresh_tokens()
                headers["Authorization"] = f"Bearer {access_token}"
                async with session.get(url, headers=headers) as retry_response:
                    return await retry_response.json() if retry_response.status == 200 else None
            return await response.json() if response.status == 200 else None

async def get_item_info(item_id: int):
    """Получает информацию о товаре и извлекает нужные данные."""
    data = await fetch_item_details(item_id)
    if data:
        return {
            "photo_url": data.get("photo_url"),
            "item_id": data.get("item_id"),
            "section": data.get("section"),
        }
    return None

async def send_to_warehouse_chat(bot, warehouse_chat_id: int, item_id: int, action: str):
    """Отправляет информацию о товаре в складской чат."""
    item_info = get_item_info(item_id)
    if item_info:
        message_text = (f"Запрос: {action}\n"
                        f"Артикул: {item_info['article']}\n"
                        f"Секция: {item_info['section']}")
        await bot.send_photo(warehouse_chat_id, item_info['photo_url'], caption=message_text)
    else:
        await bot.send_message(warehouse_chat_id, "Ошибка: не удалось получить информацию о товаре.")


# async def main():
    
#     await authenticate()
#     print(await fetch_item_details(1))
#     # await revoke_tokens()
#     # await authenticate()
#     # await print(fetch_item_details(1))



# asyncio.run(main())