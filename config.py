import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_CHATS = [-4552944230]
DATA_DIR = "chat_data"
MY_USER_ID = int(os.getenv("MY_USER_ID"))
TEST_USER_ID = int(os.getenv("TEST_USER_ID"))
PHONE_NUMBER = os.getenv("PHONE_NUMBER")

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)