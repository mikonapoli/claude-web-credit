"""Event source abstraction for input handling."""

from abc import ABC, abstractmethod
from typing import List

import tcod.event


class EventSource(ABC):
    """Abstract event source - can provide events from local input or network."""

    @abstractmethod
    async def get_events(self, timeout: float = 0.1) -> List[tcod.event.Event]:
        """Get events in tcod format.

        Args:
            timeout: Maximum time to wait for events (in seconds)

        Returns:
            List of tcod.event.Event objects
        """
        pass


class LocalEventSource(EventSource):
    """Event source that gets events from local tcod input."""

    async def get_events(self, timeout: float = 0.1) -> List[tcod.event.Event]:
        """Get events from local tcod keyboard/mouse/window.

        Args:
            timeout: Maximum time to wait for events

        Returns:
            List of tcod events
        """
        # tcod.event.wait is synchronous, but we're in async context
        # Just call it directly - it will block briefly then return
        return list(tcod.event.wait(timeout=timeout))


class WebSocketEventSource(EventSource):
    """Event source that gets events from WebSocket (browser input)."""

    def __init__(self, game_server):
        """Initialize WebSocket event source.

        Args:
            game_server: WebSocket server to receive input from
        """
        self.game_server = game_server
        self.bridge = WebSocketEventBridge()

    async def get_events(self, timeout: float = 0.1) -> List[tcod.event.Event]:
        """Get events from browser via WebSocket, converted to tcod format.

        Args:
            timeout: Maximum time to wait for events

        Returns:
            List of tcod events (converted from browser input)
        """
        # Get message from browser
        message = await self.game_server.get_input(timeout=timeout)

        if message:
            # Convert browser event to tcod event
            tcod_event = self.bridge.browser_to_tcod_event(message)
            return [tcod_event] if tcod_event else []

        return []


class WebSocketEventBridge:
    """Translates browser keyboard events to tcod events."""

    # Map browser key names to tcod KeySym values
    KEY_MAP = {
        # Arrow keys
        "ArrowUp": tcod.event.KeySym.UP,
        "ArrowDown": tcod.event.KeySym.DOWN,
        "ArrowLeft": tcod.event.KeySym.LEFT,
        "ArrowRight": tcod.event.KeySym.RIGHT,
        # Vi keys (lowercase)
        "k": tcod.event.KeySym.K,
        "j": tcod.event.KeySym.J,
        "h": tcod.event.KeySym.H,
        "l": tcod.event.KeySym.L,
        "y": tcod.event.KeySym.Y,
        "u": tcod.event.KeySym.U,
        "b": tcod.event.KeySym.B,
        "n": tcod.event.KeySym.N,
        # Vi keys (uppercase)
        "K": tcod.event.KeySym.K,
        "J": tcod.event.KeySym.J,
        "H": tcod.event.KeySym.H,
        "L": tcod.event.KeySym.L,
        "Y": tcod.event.KeySym.Y,
        "U": tcod.event.KeySym.U,
        "B": tcod.event.KeySym.B,
        "N": tcod.event.KeySym.N,
        # Action keys
        "i": tcod.event.KeySym.I,
        "g": tcod.event.KeySym.G,
        "c": tcod.event.KeySym.C,
        "d": tcod.event.KeySym.D,
        "e": tcod.event.KeySym.E,
        "m": tcod.event.KeySym.M,
        "r": tcod.event.KeySym.R,
        "s": tcod.event.KeySym.S,
        "t": tcod.event.KeySym.T,
        "x": tcod.event.KeySym.X,
        "C": tcod.event.KeySym.C,  # Uppercase C for confusion scroll test
        # Special keys
        ".": tcod.event.KeySym.PERIOD,
        ">": tcod.event.KeySym.GREATER,
        "Escape": tcod.event.KeySym.ESCAPE,
        "Enter": tcod.event.KeySym.RETURN,
        " ": tcod.event.KeySym.SPACE,
    }

    def browser_to_tcod_event(self, message_data: dict) -> tcod.event.Event:
        """Convert browser keyboard event to tcod.event.KeyDown.

        Args:
            message_data: Dict from browser like {"key": "ArrowUp", "type": "keydown", ...}

        Returns:
            tcod.event.KeyDown or tcod.event.Quit, or None if not recognized
        """
        event_type = message_data.get("type", "keydown")

        # Handle quit event
        if event_type == "quit":
            return tcod.event.Quit()

        # Handle keydown events
        if event_type == "keydown":
            key = message_data.get("key", "")

            # Get tcod KeySym (or UNKNOWN if not mapped)
            sym = self.KEY_MAP.get(key, tcod.event.KeySym.UNKNOWN)

            # Skip unknown keys
            if sym == tcod.event.KeySym.UNKNOWN:
                return None

            # Create KeyDown event
            # Note: We're creating a minimal event with just the fields InputHandler needs
            event = tcod.event.KeyDown(
                scancode=0,  # Not used by InputHandler
                sym=sym,
                mod=0,  # TODO: Add shift/ctrl/alt support if needed
                repeat=False,
            )

            return event

        return None
