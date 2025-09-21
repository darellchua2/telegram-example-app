"""
Configuration management for the Telegram bot.
Handles loading and validation of environment variables.
"""
import os
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Set
from dotenv import load_dotenv
from .auth import parse_authorized_users

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for the Telegram bot application."""

    def __init__(self):
        """Initialize configuration by loading environment variables."""
        load_dotenv()
        self._load_config()
        self._validate_config()

    def _load_config(self):
        """Load configuration from environment variables."""
        # Bot configuration
        self.bot_token = os.getenv("BOT_TOKEN")
        self.webhook_secret = os.getenv("WEBHOOK_SECRET")

        # Server configuration
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", 8000))

        # Security configuration
        authorized_users_str = os.getenv("AUTHORIZED_USERS", "")
        self.authorized_users: "Set[int]" = parse_authorized_users(authorized_users_str)

        logger.info("Configuration loaded from environment variables")

    def _validate_config(self):
        """Validate required configuration values."""
        if not self.bot_token:
            raise ValueError("BOT_TOKEN environment variable is required")

        if not self.webhook_secret:
            raise ValueError("WEBHOOK_SECRET environment variable is required")

        logger.info("Configuration validation completed successfully")

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return os.getenv("ENVIRONMENT", "development").lower() == "development"

    @property
    def log_level(self) -> str:
        """Get the logging level from environment."""
        return os.getenv("LOG_LEVEL", "INFO").upper()

    def get_config_summary(self) -> dict:
        """
        Get a summary of the current configuration (excluding sensitive data).

        Returns:
            Dictionary containing non-sensitive configuration values
        """
        return {
            "host": self.host,
            "port": self.port,
            "authorized_users_count": len(self.authorized_users),
            "is_development": self.is_development,
            "log_level": self.log_level,
            "bot_token_configured": bool(self.bot_token),
            "webhook_secret_configured": bool(self.webhook_secret)
        }


# Global configuration instance
config = Config()