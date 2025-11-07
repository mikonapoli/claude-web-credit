"""Input handling for the game."""

from enum import Enum
from typing import Optional, TYPE_CHECKING

import tcod.event

if TYPE_CHECKING:
    from roguelike.commands.command import Command
    from roguelike.commands.factory import CommandFactory


class Action(Enum):
    """Possible player actions.

    NOTE: This enum is kept for backward compatibility with existing tests
    and TurnManager. New code should use Command objects directly instead.
    """

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
    TARGETING_SELECT = "targeting_select"
    TARGETING_CANCEL = "targeting_cancel"
    TARGETING_CYCLE_NEXT = "targeting_cycle_next"
    TARGETING_CYCLE_PREV = "targeting_cycle_prev"
    TEST_CONFUSION = "test_confusion"


class InputHandler:
    """Handles keyboard input and creates Command objects.

    Uses manual event dispatching instead of deprecated EventDispatch.
    Follows the Command pattern by creating Command objects directly
    from input, eliminating the Action enum middleman.
    """

    def __init__(self, command_factory: "CommandFactory"):
        """Initialize the input handler.

        Args:
            command_factory: Factory for creating Command objects
        """
        self.command_factory = command_factory
        self.last_command: Optional["Command"] = None
        self.targeting_mode: bool = False

    def dispatch(self, event: tcod.event.Event) -> None:
        """Dispatch events to appropriate handlers.

        Args:
            event: Event to dispatch
        """
        if isinstance(event, tcod.event.Quit):
            self.ev_quit(event)
        elif isinstance(event, tcod.event.KeyDown):
            self.ev_keydown(event)

    def ev_quit(self, event: tcod.event.Quit) -> None:
        """Handle quit event.

        Args:
            event: Quit event
        """
        self.last_command = self.command_factory.create_quit_command()

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

        # Movement keys (vi keys and arrow keys)
        if key in (tcod.event.KeySym.UP, tcod.event.KeySym.K):
            self.last_command = self.command_factory.create_move_command(0, -1)
        elif key in (tcod.event.KeySym.DOWN, tcod.event.KeySym.J):
            self.last_command = self.command_factory.create_move_command(0, 1)
        elif key in (tcod.event.KeySym.LEFT, tcod.event.KeySym.H):
            self.last_command = self.command_factory.create_move_command(-1, 0)
        elif key in (tcod.event.KeySym.RIGHT, tcod.event.KeySym.L):
            self.last_command = self.command_factory.create_move_command(1, 0)

        # Diagonal movement (vi keys)
        elif key == tcod.event.KeySym.Y:
            self.last_command = self.command_factory.create_move_command(-1, -1)
        elif key == tcod.event.KeySym.U:
            self.last_command = self.command_factory.create_move_command(1, -1)
        elif key == tcod.event.KeySym.B:
            self.last_command = self.command_factory.create_move_command(-1, 1)
        elif key == tcod.event.KeySym.N:
            self.last_command = self.command_factory.create_move_command(1, 1)

        # Wait/skip turn
        elif key == tcod.event.KeySym.PERIOD and not event.mod & tcod.event.KMOD_SHIFT:
            self.last_command = self.command_factory.create_wait_command()

        # Descend stairs (> key, which is shift + period)
        elif key == tcod.event.KeySym.PERIOD and event.mod & tcod.event.KMOD_SHIFT:
            self.last_command = self.command_factory.create_descend_stairs_command()

        # Pickup item
        elif key == tcod.event.KeySym.G:
            self.last_command = self.command_factory.create_pickup_command()

        # Inventory
        elif key == tcod.event.KeySym.I:
            # TODO: Create inventory command once we have inventory UI
            self.last_command = None

        # Test: Confusion scroll targeting (C key)
        elif key == tcod.event.KeySym.C:
            # TODO: Create confusion targeting command
            self.last_command = None

        # Quit
        elif key == tcod.event.KeySym.ESCAPE:
            self.last_command = self.command_factory.create_quit_command()

    def _handle_targeting_keys(self, event: tcod.event.KeyDown) -> None:
        """Handle keydown in targeting mode.

        Args:
            event: KeyDown event
        """
        key = event.sym

        # Movement keys move cursor
        if key in (tcod.event.KeySym.UP, tcod.event.KeySym.K):
            self.last_command = self.command_factory.create_targeting_move_command(0, -1)
        elif key in (tcod.event.KeySym.DOWN, tcod.event.KeySym.J):
            self.last_command = self.command_factory.create_targeting_move_command(0, 1)
        elif key in (tcod.event.KeySym.LEFT, tcod.event.KeySym.H):
            self.last_command = self.command_factory.create_targeting_move_command(-1, 0)
        elif key in (tcod.event.KeySym.RIGHT, tcod.event.KeySym.L):
            self.last_command = self.command_factory.create_targeting_move_command(1, 0)

        # Diagonal movement
        elif key == tcod.event.KeySym.Y:
            self.last_command = self.command_factory.create_targeting_move_command(-1, -1)
        elif key == tcod.event.KeySym.U:
            self.last_command = self.command_factory.create_targeting_move_command(1, -1)
        elif key == tcod.event.KeySym.B:
            self.last_command = self.command_factory.create_targeting_move_command(-1, 1)
        elif key == tcod.event.KeySym.N:
            self.last_command = self.command_factory.create_targeting_move_command(1, 1)

        # Tab cycles through targets
        elif key == tcod.event.KeySym.TAB:
            if event.mod & tcod.event.KMOD_SHIFT:
                self.last_command = self.command_factory.create_targeting_cycle_command(forward=False)
            else:
                self.last_command = self.command_factory.create_targeting_cycle_command(forward=True)

        # Enter/Return selects target
        elif key in (tcod.event.KeySym.RETURN, tcod.event.KeySym.RETURN2):
            self.last_command = self.command_factory.create_targeting_select_command()

        # Escape cancels targeting
        elif key == tcod.event.KeySym.ESCAPE:
            self.last_command = self.command_factory.create_targeting_cancel_command()

    def set_targeting_mode(self, enabled: bool) -> None:
        """Enable or disable targeting mode.

        Args:
            enabled: True to enable targeting mode
        """
        self.targeting_mode = enabled

    def get_command(self) -> Optional["Command"]:
        """Get the last command and clear it.

        Returns:
            Last command or None
        """
        command = self.last_command
        self.last_command = None
        return command
