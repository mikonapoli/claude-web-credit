"""Presentation context abstraction for rendering output."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import tcod.console

if TYPE_CHECKING:
    import tcod.context


class PresentationContext(ABC):
    """Abstract presentation context - can present locally or remotely."""

    @abstractmethod
    def present(self, console: tcod.console.Console) -> None:
        """Present the console to the target (local window or network).

        Args:
            console: The tcod Console to present
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the presentation context."""
        pass


class TcodPresentationContext(PresentationContext):
    """Presentation context for local tcod window."""

    def __init__(self, tcod_context: "tcod.context.Context"):
        """Initialize with existing tcod context.

        Args:
            tcod_context: The tcod.context.Context for window presentation
        """
        self.tcod_context = tcod_context

    def present(self, console: tcod.console.Console) -> None:
        """Present console to local window.

        Args:
            console: Console to present
        """
        self.tcod_context.present(console)

    def close(self) -> None:
        """Close the tcod window."""
        self.tcod_context.close()


class WebSocketPresentationContext(PresentationContext):
    """Presentation context for WebSocket streaming to browser."""

    def __init__(self, game_server, width: int, height: int):
        """Initialize WebSocket presentation context.

        Args:
            game_server: WebSocket server to broadcast frames to
            width: Console width in characters
            height: Console height in characters
        """
        self.game_server = game_server
        self.width = width
        self.height = height
        self._prev_tiles = None  # For delta encoding optimization

    def present(self, console: tcod.console.Console) -> None:
        """Send console state to browser clients via WebSocket.

        Args:
            console: Console to serialize and send
        """
        import asyncio

        # Serialize console data
        frame_data = self._serialize_console(console)

        # Send to all connected clients (non-blocking)
        asyncio.create_task(self.game_server.broadcast(frame_data))

    def _serialize_console(self, console: tcod.console.Console) -> dict:
        """Extract console state as JSON-serializable dict.

        Args:
            console: Console to serialize

        Returns:
            Dict with console state (full frame or delta)
        """
        tiles = console._tiles

        # For now, always send full frame
        # TODO: Implement delta encoding for bandwidth optimization
        return {
            "type": "frame",
            "width": self.width,
            "height": self.height,
            "tiles": {
                "ch": tiles["ch"].tolist(),
                "fg": tiles["fg"].tolist(),
                "bg": tiles["bg"].tolist(),
            },
        }

    def close(self) -> None:
        """Notify browser clients that session is closing."""
        import asyncio

        # Send close notification to clients
        asyncio.create_task(
            self.game_server.broadcast({"type": "close"})
        )
