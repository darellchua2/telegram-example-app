from fastapi import FastAPI, Request, HTTPException
from telegram import Update
from telegram.ext import Application
import json
import logging

from utils.config import config
from utils.auth import AuthManager
from utils.telegram_handlers import TelegramHandlers
from models.webhook import WebhookResponse

logging.basicConfig(level=getattr(logging, config.log_level, logging.INFO))
logger = logging.getLogger(__name__)

app = FastAPI(title="Telegram Bot Webhook", description="FastAPI app for handling Telegram bot webhooks")

telegram_app = Application.builder().token(config.bot_token).build()
auth_manager = AuthManager(config.authorized_users)
handlers = TelegramHandlers(telegram_app, auth_manager)

logger.info(f"Application initialized with config: {config.get_config_summary()}")


@app.get("/")
async def root():
    return {"message": "Telegram Bot Webhook Server is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/webhook/{token}", response_model=WebhookResponse)
async def telegram_webhook(token: str, request: Request) -> WebhookResponse:
    if token != config.webhook_secret:
        logger.warning(f"Invalid webhook token received: {token}")
        raise HTTPException(status_code=403, detail="Invalid webhook token")

    try:
        body = await request.body()
        update_data = json.loads(body.decode('utf-8'))

        logger.info(f"Received update: {update_data}")

        update = Update.de_json(update_data, telegram_app.bot)

        if update.message:
            response = await handlers.process_message(update.message)
            return WebhookResponse(
                status="ok",
                response=response,
                update_type="message",
                authorized=response.get("authorized")
            )
        elif update.callback_query:
            response = await handlers.process_callback_query(update.callback_query)
            return WebhookResponse(
                status="ok",
                response=response,
                update_type="callback_query",
                authorized=response.get("authorized")
            )
        else:
            logger.info("Received update with no message or callback query")
            return WebhookResponse(
                status="ok",
                message="Update processed",
                update_type="unknown"
            )

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=config.host, port=config.port)