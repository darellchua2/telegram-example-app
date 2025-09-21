"""
Webhook-related Pydantic models for the Telegram bot.
Defines data structures for incoming webhook updates.
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class WebhookUpdate(BaseModel):
    """
    Represents a Telegram webhook update.

    This model defines the structure of incoming webhook data from Telegram.
    Only one of the optional fields will be present in each update.
    """

    update_id: int = Field(
        ...,
        description="The update's unique identifier"
    )

    message: Optional[Dict[str, Any]] = Field(
        None,
        description="New incoming message of any kind — text, photo, sticker, etc."
    )

    edited_message: Optional[Dict[str, Any]] = Field(
        None,
        description="New version of a message that is known to the bot and was edited"
    )

    channel_post: Optional[Dict[str, Any]] = Field(
        None,
        description="New incoming channel post of any kind — text, photo, sticker, etc."
    )

    edited_channel_post: Optional[Dict[str, Any]] = Field(
        None,
        description="New version of a channel post that is known to the bot and was edited"
    )

    inline_query: Optional[Dict[str, Any]] = Field(
        None,
        description="New incoming inline query"
    )

    chosen_inline_result: Optional[Dict[str, Any]] = Field(
        None,
        description="The result of an inline query that was chosen by a user and sent to their chat partner"
    )

    callback_query: Optional[Dict[str, Any]] = Field(
        None,
        description="New incoming callback query"
    )

    shipping_query: Optional[Dict[str, Any]] = Field(
        None,
        description="New incoming shipping query"
    )

    pre_checkout_query: Optional[Dict[str, Any]] = Field(
        None,
        description="New incoming pre-checkout query"
    )

    poll: Optional[Dict[str, Any]] = Field(
        None,
        description="New poll state"
    )

    poll_answer: Optional[Dict[str, Any]] = Field(
        None,
        description="A user changed their answer in a non-anonymous poll"
    )

    my_chat_member: Optional[Dict[str, Any]] = Field(
        None,
        description="The bot's chat member status was updated in a chat"
    )

    chat_member: Optional[Dict[str, Any]] = Field(
        None,
        description="A chat member's status was updated in a chat"
    )

    chat_join_request: Optional[Dict[str, Any]] = Field(
        None,
        description="A request to join the chat has been sent"
    )

    class Config:
        """Pydantic model configuration."""
        extra = "forbid"  # Don't allow extra fields
        validate_assignment = True  # Validate on assignment


class WebhookResponse(BaseModel):
    """
    Represents a response from webhook processing.
    Used for API responses and logging.
    """

    status: str = Field(
        ...,
        description="Processing status (ok, error, etc.)"
    )

    message: Optional[str] = Field(
        None,
        description="Status message or error description"
    )

    response: Optional[Dict[str, Any]] = Field(
        None,
        description="Detailed response data from handlers"
    )

    authorized: Optional[bool] = Field(
        None,
        description="Whether the request was from an authorized user"
    )

    update_type: Optional[str] = Field(
        None,
        description="Type of update processed (message, callback_query, etc.)"
    )

    class Config:
        """Pydantic model configuration."""
        extra = "forbid"
        validate_assignment = True