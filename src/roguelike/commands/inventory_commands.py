"""Inventory-related commands."""

from typing import List

from roguelike.commands.command import Command, CommandResult
from roguelike.components.combat import CombatComponent
from roguelike.components.entity import ComponentEntity
from roguelike.components.health import HealthComponent
from roguelike.components.inventory import InventoryComponent
from roguelike.components.status_effects import StatusEffectsComponent
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
        effect_applied = False

        if self.item.item_type == ItemType.HEALING_POTION:
            # Check if player has health component
            health = self.player.get_component(HealthComponent)
            if health is None:
                return CommandResult(success=False, turn_consumed=False)

            # Heal the player - only succeeds if healing was actually applied
            actual_healed = health.heal(self.item.value)
            effect_applied = actual_healed > 0

        elif self.item.item_type == ItemType.STRENGTH_POTION:
            # Apply temporary strength buff via status effect
            status_comp = self.player.get_component(StatusEffectsComponent)
            if status_comp is None:
                # Add status effects component if it doesn't exist
                status_comp = StatusEffectsComponent()
                self.player.add_component(status_comp)

            # Apply strength effect (10 turns, power bonus = item value)
            effect_applied = status_comp.add_effect("strength", duration=10, power=self.item.value)

        # Only remove item and succeed if effect was applied
        if effect_applied:
            inventory.remove_item(self.item)
            return CommandResult(success=True, turn_consumed=True)
        else:
            return CommandResult(success=False, turn_consumed=False)
