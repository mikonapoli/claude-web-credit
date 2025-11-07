"""Command factory for creating commands from input."""

from typing import List, Optional

from roguelike.commands.command import Command
from roguelike.commands.game_commands import (
    MoveCommand,
    WaitCommand,
    QuitCommand,
    DescendStairsCommand,
    ShowInventoryCommand,
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
from roguelike.ui.input_handler import Action
from roguelike.ui.message_log import MessageLog
from roguelike.utils.position import Position
from roguelike.world.fov import FOVMap
from roguelike.world.game_map import GameMap


class CommandFactory:
    """Factory for creating Command objects from Actions."""

    def __init__(
        self,
        combat_system: CombatSystem,
        movement_system: MovementSystem,
        ai_system: AISystem,
        status_effects_system: Optional[StatusEffectsSystem],
        targeting_system: TargetingSystem,
        message_log: MessageLog,
        event_bus: EventBus,
    ):
        """Initialize command factory.

        Args:
            combat_system: Combat system for resolving attacks
            movement_system: Movement system for entity movement
            ai_system: AI system for enemy behavior
            status_effects_system: Status effects system for managing effects
            targeting_system: Targeting system for targeted abilities
            message_log: Message log for displaying messages
            event_bus: Event bus for publishing events
        """
        self.combat_system = combat_system
        self.movement_system = movement_system
        self.ai_system = ai_system
        self.status_effects_system = status_effects_system
        self.targeting_system = targeting_system
        self.message_log = message_log
        self.event_bus = event_bus

    def create_command(
        self,
        action: Action,
        player: ComponentEntity,
        entities: List[ComponentEntity],
        game_map: GameMap,
        fov_map: FOVMap,
        fov_radius: int,
        stairs_pos: Optional[Position] = None,
    ) -> Optional[Command]:
        """Create a command from an action.

        Args:
            action: Action to convert
            player: The player entity
            entities: All entities in the game
            game_map: The game map
            fov_map: Field of view map
            fov_radius: FOV radius
            stairs_pos: Position of stairs (if any)

        Returns:
            Command object or None if action not recognized
        """
        # Movement commands
        movement_map = {
            Action.MOVE_UP: (0, -1),
            Action.MOVE_DOWN: (0, 1),
            Action.MOVE_LEFT: (-1, 0),
            Action.MOVE_RIGHT: (1, 0),
            Action.MOVE_UP_LEFT: (-1, -1),
            Action.MOVE_UP_RIGHT: (1, -1),
            Action.MOVE_DOWN_LEFT: (-1, 1),
            Action.MOVE_DOWN_RIGHT: (1, 1),
        }

        if action in movement_map:
            dx, dy = movement_map[action]
            return MoveCommand(
                player=player,
                dx=dx,
                dy=dy,
                entities=entities,
                game_map=game_map,
                fov_map=fov_map,
                fov_radius=fov_radius,
                movement_system=self.movement_system,
                combat_system=self.combat_system,
                ai_system=self.ai_system,
                status_effects_system=self.status_effects_system,
            )

        # Other commands
        if action == Action.WAIT:
            return WaitCommand(
                player=player,
                entities=entities,
                ai_system=self.ai_system,
                combat_system=self.combat_system,
                status_effects_system=self.status_effects_system,
            )
        elif action == Action.QUIT:
            return QuitCommand()
        elif action == Action.DESCEND_STAIRS:
            return DescendStairsCommand(
                player=player,
                stairs_pos=stairs_pos,
                message_log=self.message_log,
            )
        elif action == Action.INVENTORY:
            return ShowInventoryCommand()

        # Targeting commands
        if self.targeting_system.is_active:
            if action in movement_map:
                dx, dy = movement_map[action]
                return TargetingMoveCommand(
                    targeting_system=self.targeting_system,
                    dx=dx,
                    dy=dy,
                )
            elif action == Action.TARGETING_SELECT:
                return TargetingSelectCommand(
                    targeting_system=self.targeting_system,
                )
            elif action == Action.TARGETING_CANCEL:
                return TargetingCancelCommand(
                    targeting_system=self.targeting_system,
                )
            elif action in (Action.TARGETING_CYCLE_NEXT, Action.TARGETING_CYCLE_PREV):
                forward = action == Action.TARGETING_CYCLE_NEXT
                return TargetingCycleCommand(
                    targeting_system=self.targeting_system,
                    forward=forward,
                )

        return None
