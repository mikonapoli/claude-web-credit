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
    INVENTORY_USE = "inventory_use"
    INVENTORY_DROP = "inventory_drop"
    QUIT = "quit"
    TARGETING_SELECT = "targeting_select"
    TARGETING_CANCEL = "targeting_cancel"
    TARGETING_CYCLE_NEXT = "targeting_cycle_next"
    TARGETING_CYCLE_PREV = "targeting_cycle_prev"
    TEST_CONFUSION = "test_confusion"


class InputHandler(tcod.event.EventDispatch):
    """Handles keyboard input."""

    def __init__(self):
        """Initialize the input handler."""
        self.last_action: Optional[Action] = None
        self.targeting_mode: bool = False
        self.inventory_mode: bool = False
        self.inventory_drop_mode: bool = False
        self.selected_item_letter: Optional[str] = None

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

        # Targeting mode has different key bindings
        if self.targeting_mode:
            self._handle_targeting_keys(event)
            return

        # Inventory mode has different key bindings
        if self.inventory_mode:
            self._handle_inventory_keys(event)
            return

        # Movement keys (vi keys and arrow keys)
        if key in (tcod.event.KeySym.UP, tcod.event.KeySym.K):
            self.last_action = Action.MOVE_UP
        elif key in (tcod.event.KeySym.DOWN, tcod.event.KeySym.J):
            self.last_action = Action.MOVE_DOWN
        elif key in (tcod.event.KeySym.LEFT, tcod.event.KeySym.H):
            self.last_action = Action.MOVE_LEFT
        elif key in (tcod.event.KeySym.RIGHT, tcod.event.KeySym.L):
            self.last_action = Action.MOVE_RIGHT

        # Diagonal movement (vi keys)
        elif key == tcod.event.KeySym.Y:
            self.last_action = Action.MOVE_UP_LEFT
        elif key == tcod.event.KeySym.U:
            self.last_action = Action.MOVE_UP_RIGHT
        elif key == tcod.event.KeySym.B:
            self.last_action = Action.MOVE_DOWN_LEFT
        elif key == tcod.event.KeySym.N:
            self.last_action = Action.MOVE_DOWN_RIGHT

        # Wait/skip turn
        elif key == tcod.event.KeySym.PERIOD and not event.mod & tcod.event.KMOD_SHIFT:
            self.last_action = Action.WAIT

        # Descend stairs (> key, which is shift + period)
        elif key == tcod.event.KeySym.PERIOD and event.mod & tcod.event.KMOD_SHIFT:
            self.last_action = Action.DESCEND_STAIRS
        # Pickup item
        elif key == tcod.event.KeySym.G:
            self.last_action = Action.PICKUP

        # Inventory
        elif key == tcod.event.KeySym.I:
            self.last_action = Action.INVENTORY

        # Test: Confusion scroll targeting (C key)
        elif key == tcod.event.KeySym.C:
            self.last_action = Action.TEST_CONFUSION

        # Quit
        elif key == tcod.event.KeySym.ESCAPE:
            self.last_action = Action.QUIT

    def _handle_targeting_keys(self, event: tcod.event.KeyDown) -> None:
        """Handle keydown in targeting mode.

        Args:
            event: KeyDown event
        """
        key = event.sym

        # Movement keys move cursor
        if key in (tcod.event.KeySym.UP, tcod.event.KeySym.K):
            self.last_action = Action.MOVE_UP
        elif key in (tcod.event.KeySym.DOWN, tcod.event.KeySym.J):
            self.last_action = Action.MOVE_DOWN
        elif key in (tcod.event.KeySym.LEFT, tcod.event.KeySym.H):
            self.last_action = Action.MOVE_LEFT
        elif key in (tcod.event.KeySym.RIGHT, tcod.event.KeySym.L):
            self.last_action = Action.MOVE_RIGHT

        # Diagonal movement
        elif key == tcod.event.KeySym.Y:
            self.last_action = Action.MOVE_UP_LEFT
        elif key == tcod.event.KeySym.U:
            self.last_action = Action.MOVE_UP_RIGHT
        elif key == tcod.event.KeySym.B:
            self.last_action = Action.MOVE_DOWN_LEFT
        elif key == tcod.event.KeySym.N:
            self.last_action = Action.MOVE_DOWN_RIGHT

        # Tab cycles through targets
        elif key == tcod.event.KeySym.TAB:
            if event.mod & tcod.event.KMOD_SHIFT:
                self.last_action = Action.TARGETING_CYCLE_PREV
            else:
                self.last_action = Action.TARGETING_CYCLE_NEXT

        # Enter/Return selects target
        elif key in (tcod.event.KeySym.RETURN, tcod.event.KeySym.RETURN2):
            self.last_action = Action.TARGETING_SELECT

        # Escape cancels targeting
        elif key == tcod.event.KeySym.ESCAPE:
            self.last_action = Action.TARGETING_CANCEL

    def _handle_inventory_keys(self, event: tcod.event.KeyDown) -> None:
        """Handle keydown in inventory mode.

        Args:
            event: KeyDown event
        """
        key = event.sym

        # Escape closes inventory
        if key == tcod.event.KeySym.ESCAPE:
            self.last_action = Action.INVENTORY
            return

        # Check if 'd' is pressed (drop mode)
        if key == tcod.event.KeySym.D:
            self.inventory_drop_mode = True
            return

        # Check for letter keys (a-z)
        if tcod.event.KeySym.A <= key <= tcod.event.KeySym.Z:
            # Convert key to letter
            letter = chr(key).lower()
            self.selected_item_letter = letter

            # Determine action based on mode
            if self.inventory_drop_mode:
                self.last_action = Action.INVENTORY_DROP
                self.inventory_drop_mode = False  # Reset drop mode
            else:
                self.last_action = Action.INVENTORY_USE

    def set_targeting_mode(self, enabled: bool) -> None:
        """Enable or disable targeting mode.

        Args:
            enabled: True to enable targeting mode
        """
        self.targeting_mode = enabled

    def set_inventory_mode(self, enabled: bool) -> None:
        """Enable or disable inventory mode.

        Args:
            enabled: True to enable inventory mode
        """
        self.inventory_mode = enabled
        if not enabled:
            self.inventory_drop_mode = False
            self.selected_item_letter = None

    def get_selected_item_letter(self) -> Optional[str]:
        """Get the selected item letter and clear it.

        Returns:
            Selected item letter or None
        """
        letter = self.selected_item_letter
        self.selected_item_letter = None
        return letter

    def get_action(self) -> Optional[Action]:
        """Get the last action and clear it.

        Returns:
            Last action or None
        """
        action = self.last_action
        self.last_action = None
        return action
