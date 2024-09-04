# Expense Tracking Telegram Bot

This project is a Telegram bot that helps groups track and manage their shared expenses. It uses natural language processing to analyze chat messages and extract expense information, calculates settlements, and provides an API for interacting with the bot.

## Features

- Analyze chat messages to extract expense information
- Track expenses for group members
- Calculate settlements between group members
- Provide API endpoints for retrieving group information and processing messages

## Technologies Used

- Python 3.x
- FastAPI
- Telethon (Telegram client library)
- SQLAlchemy (ORM)
- OpenAI GPT-4 (for natural language processing)
- PostgreSQL (database)

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   Create a `.env` file in the root directory and add the following variables:
   ```
   API_ID=your_telegram_api_id
   API_HASH=your_telegram_api_hash
   BOT_TOKEN=your_telegram_bot_token
   OPENAI_API_KEY=your_openai_api_key
   DATABASE_URL=your_database_url
   MY_USER_ID=your_telegram_user_id
   TEST_USER_ID=test_user_telegram_id
   PHONE_NUMBER=your_phone_number
   ```

4. Initialize the database:
   ```
   python -c "from database import init_db; init_db()"
   ```

## Running the Application

To start the bot and API server, run:
