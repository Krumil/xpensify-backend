import os
import json
from telethon.tl.types import Message
from models import ChatMessage
from agent import format_chats_to_structured_json
from config import DATA_DIR

# In-memory chat storage
chats = {}

async def process_messages(client, chat_id):
	chat = await client.get_entity(chat_id)
	messages = []
	members = []
	
	last_processed = chats.get(chat_id, {}).get("last_processed")
	
	async for participant in client.iter_participants(chat):
		if not participant.bot:
			members.append(participant.id)
	
	async for message in client.iter_messages(chat, offset_date=last_processed, reverse=True):
		if (isinstance(message, Message) and 
			message.text and 
			not message.text.startswith('/') and 
			not message.sender.bot):
			messages.append(ChatMessage(
				role="user",
				content={
					"message_id": message.id,
					"text": message.text,
					"date": message.date.isoformat(),
					"from_user": str(message.sender_id) if message.sender_id else None
				}
			))

	if messages:
		file_path = os.path.join(DATA_DIR, f"{chat_id}_messages.json")
		with open(file_path, "w") as f:
			serializable_messages = [msg.dict() for msg in messages]
			json.dump(serializable_messages, f, indent=4)

		processed_group = format_chats_to_structured_json(messages, members, chat_id)
		
		print(f"Saved {len(messages)} messages for chat {chat_id}")

	# chats[chat_id] = {"last_processed": datetime.now()}
	return processed_group