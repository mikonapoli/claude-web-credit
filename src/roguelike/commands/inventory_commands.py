"""Inventory-related commands."""

from typing import TYPE_CHECKING, List

from roguelike.commands.command import Command, CommandResult
from roguelike.components.entity import ComponentEntity
from roguelike.components.health import HealthComponent
from roguelike.components.inventory import InventoryComponent
from roguelike.entities.entity import Entity
from roguelike.entities.item import Item, ItemType

if TYPE_CHECKING:
    from roguelike.systems.crafting import CraftingSystem


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

        Note: This command does not support targeted items (confusion/fireball/lightning scrolls).
        Targeted items must be handled through a targeting flow that provides a target.

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

        # Check if item requires targeting - cannot use via this command
        if self.item.requires_targeting():
            # Targeted items need special handling - fail gracefully
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


class CraftCommand(Command):
    """Command to craft items from ingredients."""

    def __init__(
        self,
        player: ComponentEntity,
        ingredients: List[ComponentEntity],
        crafting_system: "CraftingSystem",
    ):
        """Initialize craft command.

        Args:
            player: Player entity (crafter)
            ingredients: List of ingredient entities
            crafting_system: Crafting system to use
        """
        self.player = player
        self.ingredients = ingredients
        self.crafting_system = crafting_system

    def execute(self) -> CommandResult:
        """Execute the craft command.

        Returns:
            CommandResult indicating success/failure
        """
        # Check if player has inventory component
        inventory = self.player.get_component(InventoryComponent)
        if inventory is None:
            return CommandResult(success=False, turn_consumed=False)

        # Verify all ingredients are in inventory
        inventory_items = inventory.get_items()
        for ingredient in self.ingredients:
            if ingredient not in inventory_items:
                return CommandResult(success=False, turn_consumed=False)

        # Attempt crafting
        result, consumed = self.crafting_system.craft(
            self.ingredients, crafter=self.player
        )

        if result is None:
            # Crafting failed (no matching recipe)
            return CommandResult(success=False, turn_consumed=False)

        # Remove consumed ingredients from inventory
        for ingredient in consumed:
            inventory.remove_item(ingredient)

        # Add crafted item to inventory
        if not inventory.add_item(result):
            # Inventory full - drop crafted item at player position
            # This shouldn't happen often, but handle gracefully
            result.move_to(self.player.position)
            # Note: In a full implementation, we'd add the item to the world entities
            return CommandResult(success=True, turn_consumed=True, data={"dropped": True, "result": result})

        return CommandResult(success=True, turn_consumed=True, data={"result": result})
