"""
Telegram message and callback handlers.
Contains the business logic for processing Telegram updates.
"""
import logging
from telegram import Update
from telegram.ext import Application
from .auth import AuthManager

logger = logging.getLogger(__name__)


class TelegramHandlers:
    """Handles Telegram messages and callback queries."""

    def __init__(self, telegram_app: Application, auth_manager: AuthManager):
        """
        Initialize the handlers.

        Args:
            telegram_app: Telegram Application instance
            auth_manager: Authorization manager instance
        """
        self.telegram_app = telegram_app
        self.auth_manager = auth_manager

    async def process_message(self, message) -> dict:
        """
        Process incoming Telegram messages.

        Args:
            message: Telegram message object

        Returns:
            Dictionary containing processing result
        """
        chat_id = message.chat.id
        user_id = message.from_user.id if message.from_user else None
        username = message.from_user.username if message.from_user else "Unknown"
        text = message.text or ""

        logger.info(f"Processing message from user {user_id} (@{username}) in chat {chat_id}: {text}")

        if user_id is None:
            logger.warning("Received message with no user information")
            return {"error": "No user information"}

        # Check authorization
        if not self.auth_manager.is_user_authorized(user_id):
            self.auth_manager.log_authorization_attempt(user_id, username, False, "message")
            response_text = self.auth_manager.get_unauthorized_message()
            try:
                await self.telegram_app.bot.send_message(chat_id=chat_id, text=response_text)
                return {"message_sent": response_text, "authorized": False}
            except Exception as e:
                logger.error(f"Failed to send unauthorized message: {str(e)}")
                return {"error": "Failed to send message", "authorized": False}

        self.auth_manager.log_authorization_attempt(user_id, username, True, "message")

        # Process authorized message
        response_text = await self._handle_command(text, user_id, username)

        try:
            await self.telegram_app.bot.send_message(chat_id=chat_id, text=response_text)
            return {"message_sent": response_text, "authorized": True}
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            return {"error": "Failed to send message", "authorized": True}

    async def process_callback_query(self, callback_query) -> dict:
        """
        Process incoming callback queries (button clicks).

        Args:
            callback_query: Telegram callback query object

        Returns:
            Dictionary containing processing result
        """
        query_id = callback_query.id
        chat_id = callback_query.message.chat.id
        user_id = callback_query.from_user.id if callback_query.from_user else None
        username = callback_query.from_user.username if callback_query.from_user else "Unknown"
        data = callback_query.data

        logger.info(f"Processing callback query {query_id} from user {user_id} (@{username}) with data: {data}")

        if user_id is None:
            logger.warning("Received callback query with no user information")
            return {"error": "No user information"}

        # Check authorization
        if not self.auth_manager.is_user_authorized(user_id):
            self.auth_manager.log_authorization_attempt(user_id, username, False, "callback")
            try:
                await self.telegram_app.bot.answer_callback_query(callback_query_id=query_id, text="🚫 Unauthorized")
                return {"callback_processed": data, "authorized": False}
            except Exception as e:
                logger.error(f"Failed to respond to unauthorized callback query: {str(e)}")
                return {"error": "Failed to process callback query", "authorized": False}

        self.auth_manager.log_authorization_attempt(user_id, username, True, "callback")

        # Process authorized callback
        try:
            await self.telegram_app.bot.answer_callback_query(callback_query_id=query_id, text="Button clicked!")
            await self.telegram_app.bot.send_message(chat_id=chat_id, text=f"You clicked: {data}")
            return {"callback_processed": data, "authorized": True}
        except Exception as e:
            logger.error(f"Failed to process callback query: {str(e)}")
            return {"error": "Failed to process callback query", "authorized": True}

    async def _handle_command(self, text: str, user_id: int, username: str) -> str:
        """
        Handle different bot commands.

        Args:
            text: Message text
            user_id: User ID
            username: Username

        Returns:
            Response text to send back
        """
        if text.startswith("/start"):
            return "Hello! I'm your Telegram bot. How can I help you?"

        elif text.startswith("/help"):
            return (
                "Available commands:\n"
                "/start - Start the bot\n"
                "/help - Show this help message\n"
                "/echo <text> - Echo your message\n"
                "/whoami - Show your user information"
            )

        elif text.startswith("/echo"):
            echo_text = text[5:].strip()
            return f"You said: {echo_text}" if echo_text else "Please provide text to echo"

        elif text.startswith("/whoami"):
            return f"Your user ID: {user_id}\nUsername: @{username}"

        else:
            return f"You sent: {text}\nUse /help to see available commands"