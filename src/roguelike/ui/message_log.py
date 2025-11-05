"""Message log system for displaying game messages."""

from collections import deque
from typing import Deque


class MessageLog:
    """Manages game messages with history and display limits."""

    def __init__(self, max_messages: int = 100):
        """Initialize the message log.

        Args:
            max_messages: Maximum number of messages to store in history
        """
        self.max_messages = max_messages
        self.messages: Deque[str] = deque(maxlen=max_messages)

    def add_message(self, message: str) -> None:
        """Add a new message to the log.

        Args:
            message: The message text to add
        """
        if message:
            self.messages.append(message)

    def get_messages(self, count: int | None = None) -> list[str]:
        """Get the most recent messages.

        Args:
            count: Number of recent messages to retrieve (None for all)

        Returns:
            List of recent messages, newest first
        """
        if count is None:
            return list(reversed(self.messages))
        return list(reversed(list(self.messages)[-count:]))

    def clear(self) -> None:
        """Clear all messages from the log."""
        self.messages.clear()

    @property
    def message_count(self) -> int:
        """Get the total number of messages currently stored."""
        return len(self.messages)
