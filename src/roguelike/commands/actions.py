"""Concrete action commands."""

from typing import List

from roguelike.commands.command import Command, CommandResult
from roguelike.engine.events import EventBus, ItemPickupEvent
from roguelike.entities.entity import Entity
from roguelike.entities.item import Item
from roguelike.entities.player import Player
from roguelike.systems.item_system import ItemSystem
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


class PickupItemCommand(Command):
    """Command to pick up an item."""

    def __init__(
        self,
        player: Player,
        items: List[Item],
        event_bus: EventBus,
    ):
        """Initialize pickup item command.

        Args:
            player: Player entity
            items: All items in game
            event_bus: Event bus for publishing events
        """
        self.player = player
        self.items = items
        self.event_bus = event_bus

    def execute(self) -> CommandResult:
        """Execute the pickup command."""
        # Find items at player's position
        items_here = [
            item for item in self.items if item.position == self.player.position
        ]

        if not items_here:
            return CommandResult(
                success=False, turn_consumed=False, should_quit=False
            )

        # Pick up first item
        item = items_here[0]

        # Check if inventory is full
        if self.player.inventory.is_full():
            return CommandResult(
                success=False, turn_consumed=False, should_quit=False
            )

        # Add to inventory and remove from map
        self.player.inventory.add(item)
        self.items.remove(item)

        # Emit pickup event
        self.event_bus.emit(
            ItemPickupEvent(entity_name=self.player.name, item_name=item.name)
        )

        return CommandResult(success=True, turn_consumed=True, should_quit=False)


class UseItemCommand(Command):
    """Command to use an item from inventory."""

    def __init__(
        self,
        player: Player,
        item_index: int,
        item_system: ItemSystem,
        game_map: GameMap | None = None,
        fov_map: FOVMap | None = None,
    ):
        """Initialize use item command.

        Args:
            player: Player entity
            item_index: Index of item in inventory to use
            item_system: Item system for handling effects
            game_map: Optional game map for teleportation effects
            fov_map: Optional FOV map for magic mapping effects
        """
        self.player = player
        self.item_index = item_index
        self.item_system = item_system
        self.game_map = game_map
        self.fov_map = fov_map

    def execute(self) -> CommandResult:
        """Execute the use item command.

        Note: This command does not support targeted items (confusion/fireball/lightning scrolls).
        Targeted items must be handled through a targeting flow that provides a target.
        """
        # Get item from inventory
        item = self.player.inventory.get_item_by_index(self.item_index)

        if not item:
            return CommandResult(
                success=False, turn_consumed=False, should_quit=False
            )

        # Check if item requires targeting - cannot use via this command
        if item.requires_targeting():
            # Targeted items need special handling - fail gracefully
            return CommandResult(
                success=False, turn_consumed=False, should_quit=False
            )

        # Use the item (non-targeted items only)
        success = self.item_system.use_item(
            item, self.player, self.player.inventory,
            game_map=self.game_map, fov_map=self.fov_map
        )

        return CommandResult(
            success=success, turn_consumed=success, should_quit=False
        )
