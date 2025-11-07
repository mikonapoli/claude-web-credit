"""Command factory for creating commands from input."""

from typing import List, Optional

from roguelike.commands.command import Command
from roguelike.commands.game_commands import (
    MoveCommand,
    WaitCommand,
    QuitCommand,
    DescendStairsCommand,
    PickupItemCommand,
    TargetingMoveCommand,
    TargetingSelectCommand,
    TargetingCancelCommand,
    TargetingCycleCommand,
)
from roguelike.components.entity import ComponentEntity
from roguelike.engine.events import EventBus
from roguelike.systems.ai_system import AISystem
from roguelike.systems.combat_system import CombatSystem
from roguelike.systems.movement_system import MovementSystem
from roguelike.systems.status_effects import StatusEffectsSystem
from roguelike.systems.targeting import TargetingSystem
from roguelike.ui.message_log import MessageLog
from roguelike.utils.position import Position
from roguelike.world.fov import FOVMap
from roguelike.world.game_map import GameMap


class CommandFactory:
    """Factory for creating Command objects directly from input.

    This factory eliminates the Action enum middleman and creates
    Command objects directly, as recommended in Game Programming Patterns.
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
        targeting_system: TargetingSystem,
        message_log: MessageLog,
        event_bus: EventBus,
        stairs_pos: Optional[Position] = None,
    ):
        """Initialize command factory.

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
            targeting_system: Targeting system for targeted abilities
            message_log: Message log for displaying messages
            event_bus: Event bus for publishing events
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
        self.targeting_system = targeting_system
        self.message_log = message_log
        self.event_bus = event_bus
        self.stairs_pos = stairs_pos

    def update_context(
        self,
        player: Optional[ComponentEntity] = None,
        entities: Optional[List[ComponentEntity]] = None,
        stairs_pos: Optional[Position] = None,
    ) -> None:
        """Update the factory's context (player, entities, stairs position).

        Args:
            player: The player entity
            entities: All entities in the game
            stairs_pos: Position of stairs (if any)
        """
        if player is not None:
            self.player = player
        if entities is not None:
            self.entities = entities
        if stairs_pos is not None:
            self.stairs_pos = stairs_pos

    def create_move_command(self, dx: int, dy: int) -> MoveCommand:
        """Create a move command.

        Args:
            dx: X direction to move
            dy: Y direction to move

        Returns:
            MoveCommand instance
        """
        return MoveCommand(
            player=self.player,
            dx=dx,
            dy=dy,
            entities=self.entities,
            game_map=self.game_map,
            fov_map=self.fov_map,
            fov_radius=self.fov_radius,
            movement_system=self.movement_system,
            combat_system=self.combat_system,
            ai_system=self.ai_system,
            status_effects_system=self.status_effects_system,
        )

    def create_wait_command(self) -> WaitCommand:
        """Create a wait command.

        Returns:
            WaitCommand instance
        """
        return WaitCommand(
            player=self.player,
            entities=self.entities,
            ai_system=self.ai_system,
            combat_system=self.combat_system,
            status_effects_system=self.status_effects_system,
        )

    def create_quit_command(self) -> QuitCommand:
        """Create a quit command.

        Returns:
            QuitCommand instance
        """
        return QuitCommand()

    def create_descend_stairs_command(self) -> DescendStairsCommand:
        """Create a descend stairs command.

        Returns:
            DescendStairsCommand instance
        """
        return DescendStairsCommand(
            player=self.player,
            stairs_pos=self.stairs_pos,
            message_log=self.message_log,
        )

    def create_pickup_command(self) -> PickupItemCommand:
        """Create a pickup item command.

        Returns:
            PickupItemCommand instance
        """
        return PickupItemCommand(
            player=self.player,
            entities=self.entities,
            message_log=self.message_log,
        )

    def create_targeting_move_command(self, dx: int, dy: int) -> TargetingMoveCommand:
        """Create a targeting cursor move command.

        Args:
            dx: X direction to move
            dy: Y direction to move

        Returns:
            TargetingMoveCommand instance
        """
        return TargetingMoveCommand(
            targeting_system=self.targeting_system,
            dx=dx,
            dy=dy,
        )

    def create_targeting_select_command(self) -> TargetingSelectCommand:
        """Create a targeting select command.

        Returns:
            TargetingSelectCommand instance
        """
        return TargetingSelectCommand(
            targeting_system=self.targeting_system,
        )

    def create_targeting_cancel_command(self) -> TargetingCancelCommand:
        """Create a targeting cancel command.

        Returns:
            TargetingCancelCommand instance
        """
        return TargetingCancelCommand(
            targeting_system=self.targeting_system,
        )

    def create_targeting_cycle_command(self, forward: bool = True) -> TargetingCycleCommand:
        """Create a targeting cycle command.

        Args:
            forward: True to cycle forward, False to cycle backward

        Returns:
            TargetingCycleCommand instance
        """
        return TargetingCycleCommand(
            targeting_system=self.targeting_system,
            forward=forward,
        )
