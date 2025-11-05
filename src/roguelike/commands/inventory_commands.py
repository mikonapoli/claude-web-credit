"""Inventory-related commands."""

from typing import List

from roguelike.commands.command import Command, CommandResult
from roguelike.components.entity import ComponentEntity
from roguelike.components.health import HealthComponent
from roguelike.components.inventory import InventoryComponent
from roguelike.entities.entity import Entity
from roguelike.entities.item import Item, ItemType


class PickupItemCommand(Command):
    """Command to pick up an item from the ground."""

    def __init__(self, player: ComponentEntity, entities: List[Entity]):
        """Initialize pickup command.

        Args:
            player: Player entity
            entities: All entities in game
        """
        self.player = player
        self.entities = entities

    def execute(self) -> CommandResult:
        """Execute the pickup command.

        Returns:
            CommandResult indicating success/failure
        """
        # Check if player has inventory component
        inventory = self.player.get_component(InventoryComponent)
        if inventory is None:
            return CommandResult(success=False, turn_consumed=False)

        # Find items at player's position
        items_at_position = [
            entity
            for entity in self.entities
            if isinstance(entity, Item) and entity.position == self.player.position
        ]

        # No items at position
        if not items_at_position:
            return CommandResult(success=False, turn_consumed=False)

        # Try to pick up the first item
        item = items_at_position[0]

        # Check if inventory is full
        if inventory.is_full():
            return CommandResult(success=False, turn_consumed=False)

        # Add item to inventory and remove from world
        if inventory.add_item(item):
            self.entities.remove(item)
            return CommandResult(success=True, turn_consumed=True)

        return CommandResult(success=False, turn_consumed=False)


class DropItemCommand(Command):
    """Command to drop an item from inventory."""

    def __init__(self, player: ComponentEntity, item: Item, entities: List[Entity]):
        """Initialize drop command.

        Args:
            player: Player entity
            item: Item to drop
            entities: All entities in game
        """
        self.player = player
        self.item = item
        self.entities = entities

    def execute(self) -> CommandResult:
        """Execute the drop command.

        Returns:
            CommandResult indicating success/failure
        """
        # Check if player has inventory component
        inventory = self.player.get_component(InventoryComponent)
        if inventory is None:
            return CommandResult(success=False, turn_consumed=False)

        # Try to remove item from inventory
        if not inventory.remove_item(self.item):
            return CommandResult(success=False, turn_consumed=False)

        # Place item at player's position
        self.item.move_to(self.player.position)
        self.entities.append(self.item)

        return CommandResult(success=True, turn_consumed=True)


class UseItemCommand(Command):
    """Command to use/consume an item."""

    def __init__(self, player: ComponentEntity, item: Item):
        """Initialize use item command.

        Args:
            player: Player entity
            item: Item to use
        """
        self.player = player
        self.item = item

    def execute(self) -> CommandResult:
        """Execute the use item command.

        Returns:
            CommandResult indicating success/failure
        """
        # Check if player has inventory component
        inventory = self.player.get_component(InventoryComponent)
        if inventory is None:
            return CommandResult(success=False, turn_consumed=False)

        # Check if item is in inventory
        if self.item not in inventory.get_items():
            return CommandResult(success=False, turn_consumed=False)

        # Apply item effect based on item type
        if self.item.item_type == ItemType.HEALING_POTION:
            # Check if player has health component
            health = self.player.get_component(HealthComponent)
            if health is None:
                return CommandResult(success=False, turn_consumed=False)

            # Heal the player
            health.heal(self.item.value)

        # Remove item from inventory
        inventory.remove_item(self.item)

        return CommandResult(success=True, turn_consumed=True)
