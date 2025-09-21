"""
Telegram message and callback handlers.
Contains the business logic for processing Telegram updates.
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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

        # Process authorized callback with specific handlers
        try:
            # Answer the callback query first (removes loading spinner)
            await self.telegram_app.bot.answer_callback_query(
                callback_query_id=query_id,
                text="Processing..."
            )

            # Handle different button clicks based on callback_data
            if data == "main_menu":
                await self._send_main_menu(chat_id)
                response_text = "Main menu displayed"

            elif data == "help":
                response_text = (
                    "🆘 Help Information:\n\n"
                    "Available Commands:\n"
                    "• /start - Show interactive menu\n"
                    "• /menu - Open main menu\n"
                    "• /help - Show this help\n"
                    "• /whoami - Show your info\n"
                    "• /echo <text> - Echo message\n\n"
                    "💡 Tip: Use the buttons for quick navigation!"
                )
                await self.telegram_app.bot.send_message(chat_id=chat_id, text=response_text)

            elif data == "profile":
                response_text = f"👤 Your Profile:\n\nUser ID: {user_id}\nUsername: @{username}\nStatus: ✅ Authorized User"
                await self.telegram_app.bot.send_message(chat_id=chat_id, text=response_text)

            elif data == "stats":
                import datetime
                response_text = (
                    "📊 Bot Statistics:\n\n"
                    f"• Current time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    "• Status: 🟢 Online\n"
                    "• Your interactions: This session\n"
                    "• Bot version: 1.0.0"
                )
                await self.telegram_app.bot.send_message(chat_id=chat_id, text=response_text)

            elif data == "echo_test":
                response_text = "📝 Echo Test: Hello! This is a test message. Try typing '/echo your message' to test the echo feature!"
                await self.telegram_app.bot.send_message(chat_id=chat_id, text=response_text)

            elif data == "my_info":
                response_text = f"🔍 Your Information:\n\nTelegram ID: {user_id}\nUsername: @{username}\nAuthorization: ✅ Verified\n\nYou can use /whoami command anytime!"
                await self.telegram_app.bot.send_message(chat_id=chat_id, text=response_text)

            elif data == "random_fact":
                import random
                facts = [
                    "🦋 Butterflies taste with their feet!",
                    "🐙 Octopuses have three hearts!",
                    "🍯 Honey never spoils - it's been found in Egyptian tombs!",
                    "🧠 Your brain uses about 20% of your total energy!",
                    "🌙 A day on Venus is longer than its year!"
                ]
                response_text = f"🎲 Random Fact:\n\n{random.choice(facts)}"
                await self.telegram_app.bot.send_message(chat_id=chat_id, text=response_text)

            elif data == "server_time":
                import datetime
                response_text = f"⏰ Server Time:\n\n{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                await self.telegram_app.bot.send_message(chat_id=chat_id, text=response_text)

            elif data == "back_to_start":
                await self._send_welcome_with_buttons(chat_id)
                response_text = "Returned to start menu"

            else:
                # Unknown button click
                response_text = f"🤔 Unknown button: {data}"
                await self.telegram_app.bot.send_message(
                    chat_id=chat_id,
                    text=f"🤔 I don't know how to handle: {data}"
                )

            return {"callback_processed": data, "response": response_text, "authorized": True}

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
            await self._send_welcome_with_buttons(user_id)
            return "Welcome message with interactive buttons sent!"

        elif text.startswith("/menu"):
            await self._send_main_menu(user_id)
            return "Main menu displayed"

        elif text.startswith("/help"):
            return (
                "Available commands:\n"
                "/start - Start the bot with interactive menu\n"
                "/menu - Show main menu\n"
                "/help - Show this help message\n"
                "/echo <text> - Echo your message\n"
                "/whoami - Show your user information\n\n"
                "💡 Tip: Use /start to see interactive buttons!"
            )

        elif text.startswith("/echo"):
            echo_text = text[5:].strip()
            return f"You said: {echo_text}" if echo_text else "Please provide text to echo"

        elif text.startswith("/whoami"):
            return f"Your user ID: {user_id}\nUsername: @{username}"

        else:
            return f"You sent: {text}\nUse /help to see available commands"

    async def _send_welcome_with_buttons(self, chat_id: int):
        """Send welcome message with inline keyboard buttons."""
        keyboard = [
            [
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu"),
                InlineKeyboardButton("ℹ️ Help", callback_data="help")
            ],
            [
                InlineKeyboardButton("👤 My Profile", callback_data="profile"),
                InlineKeyboardButton("📊 Stats", callback_data="stats")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await self.telegram_app.bot.send_message(
            chat_id=chat_id,
            text="🤖 Welcome! Choose an option:",
            reply_markup=reply_markup
        )

    async def _send_main_menu(self, chat_id: int):
        """Send main menu with options."""
        keyboard = [
            [
                InlineKeyboardButton("📝 Echo Test", callback_data="echo_test"),
                InlineKeyboardButton("🔍 My Info", callback_data="my_info")
            ],
            [
                InlineKeyboardButton("🎲 Random Fact", callback_data="random_fact"),
                InlineKeyboardButton("⏰ Server Time", callback_data="server_time")
            ],
            [
                InlineKeyboardButton("🔙 Back to Start", callback_data="back_to_start")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await self.telegram_app.bot.send_message(
            chat_id=chat_id,
            text="📋 Main Menu - Select an option:",
            reply_markup=reply_markup
        )