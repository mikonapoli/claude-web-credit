"""Concrete action commands."""

from typing import List

from roguelike.commands.command import Command, CommandResult
from roguelike.entities.entity import Entity
from roguelike.entities.player import Player
from roguelike.systems.turn_manager import TurnManager
from roguelike.utils.position import Position
from roguelike.world.fov import FOVMap
from roguelike.world.game_map import GameMap


class MoveCommand(Command):
    """Command to move an entity."""

    def __init__(
        self,
        turn_manager: TurnManager,
        player: Player,
        dx: int,
        dy: int,
        entities: List[Entity],
        game_map: GameMap,
        fov_map: FOVMap,
        fov_radius: int,
    ):
        """Initialize move command.

        Args:
            turn_manager: Turn manager for processing actions
            player: Player entity
            dx: X direction to move
            dy: Y direction to move
            entities: All entities in game
            game_map: The game map
            fov_map: Field of view map
            fov_radius: FOV radius
        """
        self.turn_manager = turn_manager
        self.player = player
        self.dx = dx
        self.dy = dy
        self.entities = entities
        self.game_map = game_map
        self.fov_map = fov_map
        self.fov_radius = fov_radius
        self.previous_position: Position | None = None

    def execute(self) -> CommandResult:
        """Execute the move command."""
        from roguelike.ui.input_handler import Action

        # Map direction to action
        direction_to_action = {
            (0, -1): Action.MOVE_UP,
            (0, 1): Action.MOVE_DOWN,
            (-1, 0): Action.MOVE_LEFT,
            (1, 0): Action.MOVE_RIGHT,
            (-1, -1): Action.MOVE_UP_LEFT,
            (1, -1): Action.MOVE_UP_RIGHT,
            (-1, 1): Action.MOVE_DOWN_LEFT,
            (1, 1): Action.MOVE_DOWN_RIGHT,
        }

        action = direction_to_action.get((self.dx, self.dy))
        if not action:
            return CommandResult(
                success=False, turn_consumed=False, should_quit=False
            )

        # Store previous position for undo
        self.previous_position = self.player.position

        # Execute via turn manager
        turn_consumed, should_quit = self.turn_manager.handle_player_action(
            action,
            self.player,
            self.entities,
            self.game_map,
            self.fov_map,
            self.fov_radius,
        )

        return CommandResult(
            success=turn_consumed,
            turn_consumed=turn_consumed,
            should_quit=should_quit,
        )

    def can_undo(self) -> bool:
        """Move commands can be undone."""
        return self.previous_position is not None

    def undo(self) -> None:
        """Undo the move."""
        if self.previous_position:
            self.player.move_to(self.previous_position)
            self.turn_manager.movement_system.update_fov(
                self.fov_map, self.player.position, self.fov_radius
            )


class WaitCommand(Command):
    """Command to wait/pass turn."""

    def __init__(
        self,
        turn_manager: TurnManager,
        player: Player,
        entities: List[Entity],
        game_map: GameMap,
        fov_map: FOVMap,
        fov_radius: int,
    ):
        """Initialize wait command.

        Args:
            turn_manager: Turn manager for processing actions
            player: Player entity
            entities: All entities in game
            game_map: The game map
            fov_map: Field of view map
            fov_radius: FOV radius
        """
        self.turn_manager = turn_manager
        self.player = player
        self.entities = entities
        self.game_map = game_map
        self.fov_map = fov_map
        self.fov_radius = fov_radius

    def execute(self) -> CommandResult:
        """Execute the wait command."""
        from roguelike.ui.input_handler import Action

        turn_consumed, should_quit = self.turn_manager.handle_player_action(
            Action.WAIT,
            self.player,
            self.entities,
            self.game_map,
            self.fov_map,
            self.fov_radius,
        )

        return CommandResult(
            success=True, turn_consumed=turn_consumed, should_quit=should_quit
        )


class QuitCommand(Command):
    """Command to quit the game."""

    def execute(self) -> CommandResult:
        """Execute the quit command."""
        return CommandResult(
            success=True, turn_consumed=False, should_quit=True
        )
