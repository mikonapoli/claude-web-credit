"""Crafting-related commands."""

from typing import List, Optional

from roguelike.commands.command import Command, CommandResult
from roguelike.components.entity import ComponentEntity
from roguelike.components.inventory import InventoryComponent
from roguelike.systems.crafting import CraftingSystem


class CraftItemsCommand(Command):
    """Command to craft items together."""

    def __init__(
        self,
        crafter: ComponentEntity,
        ingredients: List[ComponentEntity],
        crafting_system: CraftingSystem,
        entities: List[ComponentEntity],
    ):
        """Initialize craft command.

        Args:
            crafter: Entity performing the crafting
            ingredients: List of ingredient entities to craft
            crafting_system: Crafting system to use
            entities: All entities in game (to add crafted item)
        """
        self.crafter = crafter
        self.ingredients = ingredients
        self.crafting_system = crafting_system
        self.entities = entities

    def execute(self) -> CommandResult:
        """Execute the craft command.

        Returns:
            CommandResult indicating success/failure
        """
        # Check if crafter has inventory
        inventory = self.crafter.get_component(InventoryComponent)
        if inventory is None:
            return CommandResult(success=False, turn_consumed=False)

        # Check that all ingredients are in inventory
        for ingredient in self.ingredients:
            if ingredient not in inventory.get_items():
                return CommandResult(success=False, turn_consumed=False)

        # Attempt crafting
        result_item, consumed = self.crafting_system.craft(
            ingredients=self.ingredients,
            crafter=self.crafter,
        )

        if result_item is None:
            # Crafting failed
            return CommandResult(success=False, turn_consumed=True)

        # Remove consumed ingredients from inventory
        for consumed_ingredient in consumed:
            inventory.remove_item(consumed_ingredient)

        # Add result to inventory (or drop if full)
        if not inventory.add_item(result_item):
            # Inventory full, drop at player's feet
            result_item.move_to(self.crafter.position)
            self.entities.append(result_item)

        return CommandResult(success=True, turn_consumed=True)
