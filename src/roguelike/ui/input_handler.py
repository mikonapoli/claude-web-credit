"""Input handling for the game."""

from typing import List, Optional

import tcod.event

from roguelike.commands.command import Command
from roguelike.commands.game_commands import (
    MoveCommand,
    WaitCommand,
    QuitCommand,
    DescendStairsCommand,
    PickupItemCommand,
    StartTargetingCommand,
    TargetingMoveCommand,
    TargetingSelectCommand,
    TargetingCancelCommand,
    TargetingCycleCommand,
)
from roguelike.components.entity import ComponentEntity
from roguelike.systems.ai_system import AISystem
from roguelike.systems.combat_system import CombatSystem
from roguelike.systems.equipment_system import EquipmentSystem
from roguelike.systems.movement_system import MovementSystem
from roguelike.systems.status_effects import StatusEffectsSystem
from roguelike.systems.targeting import TargetingSystem
from roguelike.ui.message_log import MessageLog
from roguelike.utils.position import Position
from roguelike.world.fov import FOVMap
from roguelike.world.game_map import GameMap


class InputHandler:
    """Handles keyboard input and creates Command objects.

    Uses manual event dispatching instead of deprecated EventDispatch.
    Follows the Command pattern by creating Command objects directly
    from input.
    """

    def __init__(
        self,
        player: ComponentEntity,
        entities: List[ComponentEntity],
        game_map: GameMap,
        fov_map: FOVMap,
        fov_radius: int,
        combat_system: CombatSystem,
        movement_system: MovementSystem,
        ai_system: AISystem,
        status_effects_system: Optional[StatusEffectsSystem],
        equipment_system: EquipmentSystem,
        targeting_system: TargetingSystem,
        message_log: MessageLog,
        stairs_pos: Optional[Position] = None,
    ):
        """Initialize the input handler.

        Args:
            player: The player entity
            entities: All entities in the game
            game_map: The game map
            fov_map: Field of view map
            fov_radius: FOV radius
            combat_system: Combat system for resolving attacks
            movement_system: Movement system for entity movement
            ai_system: AI system for enemy behavior
            status_effects_system: Status effects system for managing effects
            equipment_system: Equipment system for managing equipment
            targeting_system: Targeting system for targeted abilities
            message_log: Message log for displaying messages
            stairs_pos: Position of stairs (if any)
        """
        self.player = player
        self.entities = entities
        self.game_map = game_map
        self.fov_map = fov_map
        self.fov_radius = fov_radius
        self.combat_system = combat_system
        self.movement_system = movement_system
        self.ai_system = ai_system
        self.status_effects_system = status_effects_system
        self.equipment_system = equipment_system
        self.targeting_system = targeting_system
        self.message_log = message_log
        self.stairs_pos = stairs_pos
        self.last_command: Optional[Command] = None
        self.targeting_mode: bool = False

    def update_context(
        self,
        player: Optional[ComponentEntity] = None,
        entities: Optional[List[ComponentEntity]] = None,
        game_map: Optional[GameMap] = None,
        fov_map: Optional[FOVMap] = None,
        stairs_pos: Optional[Position] = None,
    ) -> None:
        """Update the handler's context (player, entities, maps, stairs position).

        This is critical for level transitions where the game_map and fov_map are replaced.
        Without updating these references, commands would operate on stale map state.

        Args:
            player: The player entity
            entities: All entities in the game
            game_map: The game map
            fov_map: Field of view map
            stairs_pos: Position of stairs (if any)
        """
        if player is not None:
            self.player = player
        if entities is not None:
            self.entities = entities
        if game_map is not None:
            self.game_map = game_map
        if fov_map is not None:
            self.fov_map = fov_map
        if stairs_pos is not None:
            self.stairs_pos = stairs_pos

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
        self.last_command = QuitCommand()

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
            self.last_command = MoveCommand(
                self.player, 0, -1, self.entities, self.game_map, self.fov_map,
                self.fov_radius, self.movement_system, self.combat_system,
                self.ai_system, self.status_effects_system
            )
        elif key in (tcod.event.KeySym.DOWN, tcod.event.KeySym.J):
            self.last_command = MoveCommand(
                self.player, 0, 1, self.entities, self.game_map, self.fov_map,
                self.fov_radius, self.movement_system, self.combat_system,
                self.ai_system, self.status_effects_system
            )
        elif key in (tcod.event.KeySym.LEFT, tcod.event.KeySym.H):
            self.last_command = MoveCommand(
                self.player, -1, 0, self.entities, self.game_map, self.fov_map,
                self.fov_radius, self.movement_system, self.combat_system,
                self.ai_system, self.status_effects_system
            )
        elif key in (tcod.event.KeySym.RIGHT, tcod.event.KeySym.L):
            self.last_command = MoveCommand(
                self.player, 1, 0, self.entities, self.game_map, self.fov_map,
                self.fov_radius, self.movement_system, self.combat_system,
                self.ai_system, self.status_effects_system
            )

        # Diagonal movement (vi keys)
        elif key == tcod.event.KeySym.Y:
            self.last_command = MoveCommand(
                self.player, -1, -1, self.entities, self.game_map, self.fov_map,
                self.fov_radius, self.movement_system, self.combat_system,
                self.ai_system, self.status_effects_system
            )
        elif key == tcod.event.KeySym.U:
            self.last_command = MoveCommand(
                self.player, 1, -1, self.entities, self.game_map, self.fov_map,
                self.fov_radius, self.movement_system, self.combat_system,
                self.ai_system, self.status_effects_system
            )
        elif key == tcod.event.KeySym.B:
            self.last_command = MoveCommand(
                self.player, -1, 1, self.entities, self.game_map, self.fov_map,
                self.fov_radius, self.movement_system, self.combat_system,
                self.ai_system, self.status_effects_system
            )
        elif key == tcod.event.KeySym.N:
            self.last_command = MoveCommand(
                self.player, 1, 1, self.entities, self.game_map, self.fov_map,
                self.fov_radius, self.movement_system, self.combat_system,
                self.ai_system, self.status_effects_system
            )

        # Wait/skip turn
        elif key == tcod.event.KeySym.PERIOD and not event.mod & tcod.event.KMOD_SHIFT:
            self.last_command = WaitCommand(
                self.player, self.entities, self.ai_system,
                self.combat_system, self.status_effects_system
            )

        # Descend stairs (> key, which is shift + period)
        elif key == tcod.event.KeySym.PERIOD and event.mod & tcod.event.KMOD_SHIFT:
            self.last_command = DescendStairsCommand(
                self.player, self.stairs_pos, self.message_log
            )

        # Pickup item
        elif key == tcod.event.KeySym.G:
            self.last_command = PickupItemCommand(
                self.player, self.entities, self.message_log,
                self.ai_system, self.combat_system, self.status_effects_system
            )

        # Test: Confusion scroll targeting (C key)
        # Note: Inventory UI ('I' key) not yet implemented
        elif key == tcod.event.KeySym.C:
            self.last_command = StartTargetingCommand(
                self.player, self.entities, self.fov_map, self.targeting_system,
                self.message_log, self.game_map
            )

        # Quit
        elif key == tcod.event.KeySym.ESCAPE:
            self.last_command = QuitCommand()

    def _handle_targeting_keys(self, event: tcod.event.KeyDown) -> None:
        """Handle keydown in targeting mode.

        Args:
            event: KeyDown event
        """
        key = event.sym

        # Movement keys move cursor
        if key in (tcod.event.KeySym.UP, tcod.event.KeySym.K):
            self.last_command = TargetingMoveCommand(self.targeting_system, 0, -1)
        elif key in (tcod.event.KeySym.DOWN, tcod.event.KeySym.J):
            self.last_command = TargetingMoveCommand(self.targeting_system, 0, 1)
        elif key in (tcod.event.KeySym.LEFT, tcod.event.KeySym.H):
            self.last_command = TargetingMoveCommand(self.targeting_system, -1, 0)
        elif key in (tcod.event.KeySym.RIGHT, tcod.event.KeySym.L):
            self.last_command = TargetingMoveCommand(self.targeting_system, 1, 0)

        # Diagonal movement
        elif key == tcod.event.KeySym.Y:
            self.last_command = TargetingMoveCommand(self.targeting_system, -1, -1)
        elif key == tcod.event.KeySym.U:
            self.last_command = TargetingMoveCommand(self.targeting_system, 1, -1)
        elif key == tcod.event.KeySym.B:
            self.last_command = TargetingMoveCommand(self.targeting_system, -1, 1)
        elif key == tcod.event.KeySym.N:
            self.last_command = TargetingMoveCommand(self.targeting_system, 1, 1)

        # Tab cycles through targets
        elif key == tcod.event.KeySym.TAB:
            if event.mod & tcod.event.KMOD_SHIFT:
                self.last_command = TargetingCycleCommand(self.targeting_system, forward=False)
            else:
                self.last_command = TargetingCycleCommand(self.targeting_system, forward=True)

        # Enter/Return selects target
        elif key in (tcod.event.KeySym.RETURN, tcod.event.KeySym.RETURN2):
            self.last_command = TargetingSelectCommand(self.targeting_system)

        # Escape cancels targeting
        elif key == tcod.event.KeySym.ESCAPE:
            self.last_command = TargetingCancelCommand(self.targeting_system)

    def set_targeting_mode(self, enabled: bool) -> None:
        """Enable or disable targeting mode.

        Args:
            enabled: True to enable targeting mode
        """
        self.targeting_mode = enabled

    def get_command(self) -> Optional[Command]:
        """Get the last command and clear it.

        Returns:
            Last command or None
        """
        command = self.last_command
        self.last_command = None
        return command
