"""
Authorization utilities for the Telegram bot.
Handles user authentication and access control.
"""
import logging
from typing import Set

logger = logging.getLogger(__name__)


class AuthManager:
    """Manages user authorization for the Telegram bot."""

    def __init__(self, authorized_users: Set[int]):
        """
        Initialize the AuthManager.

        Args:
            authorized_users: Set of authorized Telegram user IDs
        """
        self.authorized_users = authorized_users
        if authorized_users:
            logger.info(f"AuthManager initialized with {len(authorized_users)} authorized users")
        else:
            logger.warning("AuthManager initialized with no authorized users - allowing all users")

    def is_user_authorized(self, user_id: int) -> bool:
        """
        Check if a user is authorized to use the bot.

        Args:
            user_id: Telegram user ID to check

        Returns:
            True if user is authorized, False otherwise
        """
        if not self.authorized_users:
            logger.warning("No authorized users configured - allowing all users")
            return True
        return user_id in self.authorized_users

    def get_unauthorized_message(self) -> str:
        """
        Get the message to send to unauthorized users.

        Returns:
            Message string for unauthorized users
        """
        return "🚫 Sorry, you are not authorized to use this bot."

    def log_authorization_attempt(self, user_id: int, username: str, authorized: bool, action: str = "access"):
        """
        Log an authorization attempt.

        Args:
            user_id: Telegram user ID
            username: Telegram username
            authorized: Whether the user was authorized
            action: Type of action attempted (e.g., "message", "callback")
        """
        if authorized:
            logger.info(f"Authorized {action} from user {user_id} (@{username})")
        else:
            logger.warning(f"Unauthorized {action} attempt from user {user_id} (@{username})")


def parse_authorized_users(authorized_users_str: str) -> Set[int]:
    """
    Parse a comma-separated string of user IDs into a set of integers.

    Args:
        authorized_users_str: Comma-separated string of user IDs

    Returns:
        Set of authorized user IDs

    Raises:
        ValueError: If the string contains invalid user IDs
    """
    if not authorized_users_str.strip():
        return set()

    try:
        return set(int(user_id.strip()) for user_id in authorized_users_str.split(",") if user_id.strip())
    except ValueError as e:
        logger.error(f"Invalid AUTHORIZED_USERS format: {e}")
        raise ValueError("AUTHORIZED_USERS must be comma-separated list of integers")