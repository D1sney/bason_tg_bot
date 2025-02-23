import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL")
AUTH_API_URL = os.getenv("AUTH_API_URL")
LOGIN_DATA = {
    "login": os.getenv("API_LOGIN"),
    "password": os.getenv("API_PASSWORD")
}
MANAGER_CHAT_ID = os.getenv("MANAGER_CHAT_ID")
WAREHOUSE_CHAT_ID = os.getenv("WAREHOUSE_CHAT_ID")
ISSUANCE_CHAT_ID = os.getenv("ISSUANCE_CHAT_ID")
SOLD_CHAT_ID = os.getenv("SOLD_CHAT_ID")
LOST_CHAT_ID = os.getenv("LOST_CHAT_ID")