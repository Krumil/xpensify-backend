import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from telethon import TelegramClient

from routes import create_router
from bot import setup_bot_handlers
from database import init_db
from config import API_ID, API_HASH, BOT_TOKEN, PHONE_NUMBER

# Load environment variables
load_dotenv()

# FastAPI app
app = FastAPI()

# Telethon clients
client = TelegramClient('user_session', API_ID, API_HASH)
bot_client = TelegramClient('bot_session', API_ID, API_HASH)

# Main function to run the bot and API
async def main():
	init_db()
	await client.start(phone=PHONE_NUMBER)
	await bot_client.start(bot_token=BOT_TOKEN)

	setup_bot_handlers(client)
	api_router = create_router(client)
	app.include_router(api_router)
	
	config = uvicorn.Config(app, host="0.0.0.0", port=8000, loop="asyncio")
	server = uvicorn.Server(config)
	await server.serve()

# Entry point
if __name__ == "__main__":
	client.loop.run_until_complete(main())