from telethon import events
from config import ALLOWED_CHATS
from message_processing import process_messages

def setup_bot_handlers(client):
    @client.on(events.NewMessage(pattern='/start'))
    async def start(event):
        print("start")
        # await event.reply("Hello! I'm here to help track expenses. Please make me an admin with 'Read all messages' permission to analyze the chat.")

    @client.on(events.NewMessage(pattern='/analyze'))
    async def analyze_now(event):
        await event.reply("Starting analysis...")
        await process_messages(event.chat_id)
        await event.reply("Analysis complete.")

# Scheduled task for message processing (commented out for now)
# async def schedule_message_processing(client):
#     while True:
#         for chat_id in ALLOWED_CHATS:
#             await process_messages(chat_id)
#         await asyncio.sleep(3600)  # Process every hour