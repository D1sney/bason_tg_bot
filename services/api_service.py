import aiohttp
import os
import json
import asyncio
import logging
from config import API_URL, AUTH_API_URL, LOGIN_DATA

# Настройка логгера для файла api_service.py
logger = logging.getLogger("api_service")
logger.setLevel(logging.INFO)

# Если обработчики еще не добавлены, добавляем их
if not logger.hasHandlers():
    file_handler = logging.FileHandler("bot.log", mode="a")
    file_handler.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

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
    logger.info("Tokens saved to %s", TOKENS_FILE)


def load_tokens():
    """Загружает AccessToken и RefreshToken из файла, если они есть."""
    global access_token, refresh_token
    if os.path.exists(TOKENS_FILE):
        with open(TOKENS_FILE, 'r') as file:
            tokens = json.load(file)
            access_token = tokens.get("access_token")
            refresh_token = tokens.get("refresh_token")
        logger.info("Tokens loaded from %s", TOKENS_FILE)
    else:
        logger.info("Tokens file %s not found", TOKENS_FILE)


async def authenticate():
    """Функция для получения AccessToken и RefreshToken через логин"""
    global access_token, refresh_token
    logger.info("Starting authentication process")
    # Сначала пытаемся загрузить токены из файла
    load_tokens()

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{AUTH_API_URL}/login/user", json=LOGIN_DATA) as response:
            data = await response.json()
            if data.get("success"):
                access_token = data["AT"]
                refresh_token = data["RT"]
                save_tokens(access_token, refresh_token)  # Сохраняем токены в файл
                logger.info("Authentication successful, tokens updated")
            elif data.get("error") == "need_captcha":
                logger.error("Authentication error: captcha required")
                raise Exception("Ошибка аутентификации: требуется пройти капчу")
            else:
                error_message = data.get("error")
                logger.error("Authentication error: %s", error_message)
                raise Exception(f"Ошибка аутентификации: {error_message}")


async def refresh_tokens():
    """Функция для обновления токенов через RefreshToken"""
    global access_token, refresh_token
    logger.info("Attempting to refresh tokens")
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{AUTH_API_URL}/refresh/user", json={"RT": refresh_token}) as response:
            data = await response.json()
            if data.get("success"):
                access_token = data["AT"]
                refresh_token = data["RT"]
                save_tokens(access_token, refresh_token)  # Сохраняем обновленные токены в файл
                logger.info("Tokens refreshed successfully")
            else:
                logger.warning("Token refresh failed, re-authenticating")
                await authenticate()


# Функция для отзыва токена (не вызывается)
async def revoke_tokens():
    """Функция для отзыва токена"""
    global access_token, refresh_token
    logger.info("Revoking tokens")
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{AUTH_API_URL}/revoke/user", json={"RT": refresh_token}) as response:
            data = await response.json()
            logger.info("Revoke tokens response: %s", data)
            print(data)


async def fetch_item_details(item_id: int):
    """Запрашивает данные о товаре по артикулу из API."""
    logger.info("Fetching details for item_id: %s", item_id)
    load_tokens()
    global access_token
    url = f"{API_URL}/getProducts"
    params = {
        "order": "desc",
        "id": item_id
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 401:  # Если AccessToken истек, обновляем
                logger.warning("Access token expired for item_id: %s, refreshing tokens", item_id)
                await refresh_tokens()
                headers["Authorization"] = f"Bearer {access_token}"
                async with session.get(url, headers=headers, params=params) as retry_response:
                    if retry_response.status == 200:
                        logger.info("Successfully fetched item details after token refresh")
                        return await retry_response.json()
                    else:
                        logger.error("Failed to fetch item details after token refresh, status: %s", retry_response.status)
                        return None
            if response.status == 200:
                logger.info("Item details fetched successfully for item_id: %s", item_id)
                return await response.json()
            else:
                logger.error("Failed to fetch item details for item_id: %s, status: %s", item_id, response.status)
                return None


async def send_to_warehouse_chat(message, warehouse_chat_id: int, manager_chat_id: int, item_id: int, action: str, warehouse_keyboard):
    """Отправляет информацию о товаре в складской чат."""
    logger.info("Sending item details to warehouse chat for item_id: %s, action: %s", item_id, action)
    item_info = await fetch_item_details(item_id)
    try:
        if len(item_info['response'][0]['result']['products']) > 0:
            product = item_info['response'][0]['result']['products'][0]
            message_text = (f"Запрос: {action}\n"
                            f"Артикул: {product['id']}\n"
                            f"Название: {product['name']}\n"
                            f"Цена: {product['price']}\n")
            await message.bot.send_message(warehouse_chat_id, message_text, reply_markup=warehouse_keyboard)
            logger.info("Message sent to warehouse chat successfully for item_id: %s", item_id)
        else:
            await message.bot.send_message(manager_chat_id, "Ошибка: не удалось получить информацию о товаре.")
            logger.error("No products found in API response for item_id: %s", item_id)
    except Exception as e:
        logger.exception("Exception in send_to_warehouse_chat for item_id: %s: %s", item_id, e)
        await message.bot.send_message(manager_chat_id, "Ошибка: произошла ошибка при обработке информации о товаре.")
