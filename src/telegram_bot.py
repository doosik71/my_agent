import os
import logging
import asyncio
from telegram import Update  # pyright: ignore[reportMissingImports]

from telegram.ext import (  # pyright: ignore[reportMissingImports]
    ApplicationBuilder, ContextTypes, MessageHandler, filters)
from dotenv import load_dotenv  # pyright: ignore[reportMissingImports]
from src.agent_core import MyAgent


# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Initialize MyAgent
agent = MyAgent(model_name=os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash"))

# Authorized user IDs
# Convert string of comma-separated IDs to a set of integers for efficient lookup
authorized_users_str = os.getenv("TELEGRAM_AUTHORIZED_USERS")
AUTHORIZED_USERS = set(
    int(uid.strip()) for uid in authorized_users_str.split(',') if uid.strip()
) if authorized_users_str else set()

# Store chat sessions per user
user_sessions = {}


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages from Telegram."""
    user_id = update.effective_user.id
    text = update.message.text

    # Check if the user is authorized
    if AUTHORIZED_USERS and user_id not in AUTHORIZED_USERS:
        logging.warning(f"Unauthorized access attempt from user ID: {user_id}")
        await update.message.reply_text("죄송합니다. 이 봇을 사용할 권한이 없습니다.")
        return

    if not text:
        return

    # Get or create chat session for this user
    if user_id not in user_sessions:
        user_sessions[user_id] = agent.client.chats.create(
            model=agent.model_name,
            config=agent.config
        )

    chat_session = user_sessions[user_id]

    # Send a typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        # Get response from MyAgent
        response_obj = agent.send_message(text, chat_session=chat_session)

        response_text = ""
        if hasattr(response_obj, 'text') and response_obj.text:
            response_text = response_obj.text
        elif hasattr(response_obj, 'candidates') and response_obj.candidates:
            for part in response_obj.candidates[0].content.parts:
                if part.text:
                    response_text += part.text
                if part.function_call:
                    # Inform user about tool calls (optional, but helpful for transparency)
                    tool_info = f"\n\n🛠️ *도구 실행:* `{part.function_call.name}`"
                    response_text += tool_info
        else:
            response_text = "죄송합니다. 응답을 생성하는 중에 문제가 발생했습니다."

        # Send response back to Telegram
        await update.message.reply_text(response_text, parse_mode=None)

    except Exception as e:
        logging.error(f"Error handling message: {e}")
        await update.message.reply_text(f"오류가 발생했습니다: {e}")


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        print("Error: TELEGRAM_BOT_TOKEN not found in .env file.")
        return

    application = ApplicationBuilder().token(token).build()

    message_handler = MessageHandler(
        filters.TEXT & (~filters.COMMAND), handle_message)
    application.add_handler(message_handler)

    print("Telegram Bot is running...")
    application.run_polling()


if __name__ == "__main__":
    main()
