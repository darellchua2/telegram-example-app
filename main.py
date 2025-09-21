from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from telegram import Update
from telegram.ext import Application
from dotenv import load_dotenv
import json
import logging
import os

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Telegram Bot Webhook", description="FastAPI app for handling Telegram bot webhooks")

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required")
if not WEBHOOK_SECRET:
    raise ValueError("WEBHOOK_SECRET environment variable is required")

telegram_app = Application.builder().token(BOT_TOKEN).build()

class WebhookUpdate(BaseModel):
    update_id: int
    message: dict = None
    edited_message: dict = None
    channel_post: dict = None
    edited_channel_post: dict = None
    inline_query: dict = None
    chosen_inline_result: dict = None
    callback_query: dict = None

@app.get("/")
async def root():
    return {"message": "Telegram Bot Webhook Server is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/webhook/{token}")
async def telegram_webhook(token: str, request: Request):
    if token != WEBHOOK_SECRET:
        logger.warning(f"Invalid webhook token received: {token}")
        raise HTTPException(status_code=403, detail="Invalid webhook token")

    try:
        body = await request.body()
        update_data = json.loads(body.decode('utf-8'))

        logger.info(f"Received update: {update_data}")

        update = Update.de_json(update_data, telegram_app.bot)

        if update.message:
            response = await process_message(update.message)
            return {"status": "ok", "response": response}
        elif update.callback_query:
            response = await process_callback_query(update.callback_query)
            return {"status": "ok", "response": response}
        else:
            logger.info("Received update with no message or callback query")
            return {"status": "ok", "message": "Update processed"}

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

async def process_message(message):
    chat_id = message.chat.id
    text = message.text or ""

    logger.info(f"Processing message from chat {chat_id}: {text}")

    if text.startswith("/start"):
        response_text = "Hello! I'm your Telegram bot. How can I help you?"
    elif text.startswith("/help"):
        response_text = "Available commands:\n/start - Start the bot\n/help - Show this help message\n/echo <text> - Echo your message"
    elif text.startswith("/echo"):
        echo_text = text[5:].strip()
        response_text = f"You said: {echo_text}" if echo_text else "Please provide text to echo"
    else:
        response_text = f"You sent: {text}\nUse /help to see available commands"

    try:
        await telegram_app.bot.send_message(chat_id=chat_id, text=response_text)
        return {"message_sent": response_text}
    except Exception as e:
        logger.error(f"Failed to send message: {str(e)}")
        return {"error": "Failed to send message"}

async def process_callback_query(callback_query):
    query_id = callback_query.id
    chat_id = callback_query.message.chat.id
    data = callback_query.data

    logger.info(f"Processing callback query {query_id} with data: {data}")

    try:
        await telegram_app.bot.answer_callback_query(callback_query_id=query_id, text="Button clicked!")
        await telegram_app.bot.send_message(chat_id=chat_id, text=f"You clicked: {data}")
        return {"callback_processed": data}
    except Exception as e:
        logger.error(f"Failed to process callback query: {str(e)}")
        return {"error": "Failed to process callback query"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT)