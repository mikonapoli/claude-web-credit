"""Input handling for the game."""

from enum import Enum
from typing import Optional

import tcod.event


class Action(Enum):
    """Possible player actions."""

    MOVE_UP = "move_up"
    MOVE_DOWN = "move_down"
    MOVE_LEFT = "move_left"
    MOVE_RIGHT = "move_right"
    MOVE_UP_LEFT = "move_up_left"
    MOVE_UP_RIGHT = "move_up_right"
    MOVE_DOWN_LEFT = "move_down_left"
    MOVE_DOWN_RIGHT = "move_down_right"
    WAIT = "wait"
    DESCEND_STAIRS = "descend_stairs"
    PICKUP = "pickup"
    INVENTORY = "inventory"
    QUIT = "quit"


class InputHandler(tcod.event.EventDispatch):
    """Handles keyboard input."""

    def __init__(self):
        """Initialize the input handler."""
        self.last_action: Optional[Action] = None

    def ev_quit(self, event: tcod.event.Quit) -> None:
        """Handle quit event.

        Args:
            event: Quit event
        """
        self.last_action = Action.QUIT

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        """Handle keydown event.

        Args:
            event: KeyDown event
        """
        key = event.sym

        # Movement keys (vi keys and arrow keys)
        if key in (tcod.event.KeySym.UP, tcod.event.KeySym.k):
            self.last_action = Action.MOVE_UP
        elif key in (tcod.event.KeySym.DOWN, tcod.event.KeySym.j):
            self.last_action = Action.MOVE_DOWN
        elif key in (tcod.event.KeySym.LEFT, tcod.event.KeySym.h):
            self.last_action = Action.MOVE_LEFT
        elif key in (tcod.event.KeySym.RIGHT, tcod.event.KeySym.l):
            self.last_action = Action.MOVE_RIGHT

        # Diagonal movement (vi keys)
        elif key == tcod.event.KeySym.y:
            self.last_action = Action.MOVE_UP_LEFT
        elif key == tcod.event.KeySym.u:
            self.last_action = Action.MOVE_UP_RIGHT
        elif key == tcod.event.KeySym.b:
            self.last_action = Action.MOVE_DOWN_LEFT
        elif key == tcod.event.KeySym.n:
            self.last_action = Action.MOVE_DOWN_RIGHT

        # Wait/skip turn
        elif key == tcod.event.KeySym.PERIOD and not event.mod & tcod.event.KMOD_SHIFT:
            self.last_action = Action.WAIT

        # Descend stairs (> key, which is shift + period)
        elif key == tcod.event.KeySym.PERIOD and event.mod & tcod.event.KMOD_SHIFT:
            self.last_action = Action.DESCEND_STAIRS
        # Pickup item
        elif key == tcod.event.KeySym.g:
            self.last_action = Action.PICKUP

        # Inventory
        elif key == tcod.event.KeySym.i:
            self.last_action = Action.INVENTORY

        # Quit
        elif key == tcod.event.KeySym.ESCAPE:
            self.last_action = Action.QUIT

    def get_action(self) -> Optional[Action]:
        """Get the last action and clear it.

        Returns:
            Last action or None
        """
        action = self.last_action
        self.last_action = None
        return action
