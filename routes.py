from fastapi import APIRouter, HTTPException, Request
from telethon.tl.functions.messages import GetCommonChatsRequest
from pydantic import BaseModel
from typing import List
from telethon.tl.types import Chat
from config import MY_USER_ID, TEST_USER_ID
from message_processing import process_messages
from database import complete_settlements

class SettlementIds(BaseModel):
    ids: List[int]

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


				# for test purposes, return the chats filtered by the allowed groups id
				allowed_groups = [4552944230]
				chats = [chat for chat in chats if chat['id'] in allowed_groups]
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

	@router.post("/complete-settlements")
	async def complete_settlements_endpoint(settlement_ids: SettlementIds):
		try:
			updated_count = complete_settlements(settlement_ids.ids)
			return {"message": f"Successfully completed {updated_count} settlements"}
		except Exception as e:
			print(e)
			raise HTTPException(status_code=500, detail=str(e))


	return router