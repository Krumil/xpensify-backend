from fastapi import APIRouter, HTTPException, Request
from telethon.tl.functions.messages import GetCommonChatsRequest
from telethon.tl.types import Chat
from config import MY_USER_ID, TEST_USER_ID
from message_processing import process_messages

def create_router(client):
	router = APIRouter()

	@router.get("/groups")
	async def get_chats(userId: int = None):
		try:
			if userId:
				if userId == MY_USER_ID:
					userId = TEST_USER_ID

				common_chats = await client(GetCommonChatsRequest(user_id=userId, max_id=0, limit=100))
				chats = [
					{
						"id": chat.id,
						"title": chat.title,
						"type": "group" if isinstance(chat, Chat) else "channel"
					}
					for chat in common_chats.chats
				]
				return {"groups": chats}
			else:
				return {"error": "You must first add the bot to the chat you want to analyze"}
			
		except Exception as e:
			print(e)
			raise HTTPException(status_code=500, detail=str(e))

	@router.post("/process-messages")
	async def process_chat_messages(request: Request):
		try:
			data = await request.json()
			chatId = data.get('chatId')
			
			if not chatId:
				raise HTTPException(status_code=400, detail="You must provide a chatId")
			
			processed_group = await process_messages(client, chatId)
			return processed_group
		except Exception as e:
			print(e)
			raise HTTPException(status_code=500, detail=str(e))

	return router