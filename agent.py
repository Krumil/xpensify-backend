from classes import ChatMessage, ExpenseTrackingOutput
from dotenv import load_dotenv
from openai import OpenAI
from typing import List
from utils import calculate_settlement
from database import (create_group, get_or_create_user, add_user_to_group, 
					  create_transaction, create_settlement, session_scope, 
					  update_group, Group, get_user_from_tgId)
import json
import os
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()

# Set up your OpenAI API key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Function to call the OpenAI API and get structured output
def format_chats_to_structured_json(messages: List[ChatMessage], members: List[int], groupId: int):
	members_str = ", ".join(str(member) for member in members)
	completion = client.beta.chat.completions.parse(
		model="gpt-4o-2024-08-06",  # Use the latest model available
		messages=[
			{
				"role": "system",
				"content": "You are an AI assistant that analyzes chat messages and extracts expense information. Format the output as a structured JSON object. Every date should be provided in the following ISO 8601 format: 'YYYY-MM-DD'."
			},
			{"role": "user", "content": f"The list of members is {members_str}. The telegram group id is {groupId}."},
			*[{"role": "user", "content": json.dumps(msg.content)} for msg in messages]
		],
		response_format= ExpenseTrackingOutput,
	)
	 
	message = completion.choices[0].message
	if message.parsed:
		result = message.parsed
	else:
		print(message.refusal)#
		return None
	output = ExpenseTrackingOutput(**result.model_dump())
	
	# Save to database
	try:
		with session_scope() as session:
			
			dbGroup = session.query(Group).filter_by(tgId=output.group.tgId).first()
			if dbGroup:
				# Update existing group
				dbGroup = update_group(output.group.tgId, output.group.name, output.group.description, output.group.currency, session=session)
			else:
				# Create new group
				dbGroup = create_group(output.group.name, output.group.description, output.group.currency, output.group.tgId, session=session)

			for member in output.group.members:
				# Create or get the user
				dbUser = get_or_create_user(member.tgId, member.username, member.firstName, member.lastName, session=session)
				
				# Add user to the group
				dbGroupMember = add_user_to_group(dbUser.id, dbGroup.id, session=session)
				
				# Create transactions for the user
				for transaction in member.transactions:
					dbTransaction = create_transaction(
						dbGroupMember.id,
						transaction.description,
						transaction.amount,
						transaction.date,
						session=session
					)
			
			# Calculate settlements
			settlements = calculate_settlement(output.model_dump())
			
			# Create settlements
			for settlement in settlements:
				payer = settlement['fromUserId']
				receiver = settlement['toUserId']
				amount = settlement['amount']
				create_settlement(payer, receiver, amount, session=session)
	
			session.commit()

	except SQLAlchemyError as e:
		print(e)
		raise

	
	# Create a new dictionary with all the data including settlements
	finalResult = output.model_dump()
	finalResult['settlements'] = settlements

	# for every group member, get the user object
	formattedMembers = []
	for member in finalResult['group']['members']:
		formattedMembers.append(get_user_from_tgId(member['tgId']))

	finalResult['group']['members'] = formattedMembers

	return finalResult