"""Crafting-related commands."""

from itertools import combinations
from typing import List, Optional

from roguelike.commands.command import Command, CommandResult
from roguelike.components.entity import ComponentEntity
from roguelike.components.inventory import InventoryComponent
from roguelike.systems.crafting import CraftingSystem
from roguelike.ui.message_log import MessageLog


class CraftCommand(Command):
    """Command to craft items from ingredients."""

    def __init__(
        self,
        player: ComponentEntity,
        ingredients: List[ComponentEntity],
        crafting_system: CraftingSystem,
        message_log: MessageLog,
    ):
        """Initialize craft command.

        Args:
            player: Player entity
            ingredients: List of ingredient entities to combine
            crafting_system: Crafting system for recipe matching
            message_log: Message log for feedback
        """
        self.player = player
        self.ingredients = ingredients
        self.crafting_system = crafting_system
        self.message_log = message_log

    def execute(self) -> CommandResult:
        """Execute the craft command.

        Returns:
            CommandResult indicating success/failure
        """
        # Check if player has inventory component
        inventory = self.player.get_component(InventoryComponent)
        if inventory is None:
            self.message_log.add_message("You have no inventory!")
            return CommandResult(success=False, turn_consumed=False)

        # Check that all ingredients are in inventory
        for ingredient in self.ingredients:
            if ingredient not in inventory.get_items():
                self.message_log.add_message(
                    f"{ingredient.name} is not in your inventory!"
                )
                return CommandResult(success=False, turn_consumed=False)

        # Check if ingredients can be crafted
        if not self.crafting_system.can_craft(self.ingredients):
            self.message_log.add_message(
                "These ingredients cannot be crafted together."
            )
            return CommandResult(success=False, turn_consumed=False)

        # Perform crafting - use player's position for spawn location
        result, consumed = self.crafting_system.craft(
            self.ingredients,
            crafter=self.player,
            position=self.player.position
        )

        if result is None:
            self.message_log.add_message("Crafting failed!")
            return CommandResult(success=False, turn_consumed=False)

        # Remove consumed ingredients from inventory
        for ingredient in consumed:
            inventory.remove_item(ingredient)

        # Add crafted item to inventory
        if not inventory.add_item(result):
            # Inventory full - drop at player's position
            # Note: We would need to add result to entities list, but
            # that's handled by the game engine's entity management
            self.message_log.add_message(
                f"Inventory full! {result.name} dropped on ground."
            )
            # For now, just fail - proper item dropping requires entity list access
            return CommandResult(success=False, turn_consumed=False)

        # Success message is handled by event system
        return CommandResult(success=True, turn_consumed=True)


class AutoCraftCommand(Command):
    """Command to automatically find and craft valid recipes from inventory.

    This command checks all possible combinations of 2-3 items in the
    player's inventory and crafts the first valid recipe found.
    """

    def __init__(
        self,
        player: ComponentEntity,
        crafting_system: CraftingSystem,
        message_log: MessageLog,
        entities: List[ComponentEntity],
    ):
        """Initialize auto craft command.

        Args:
            player: Player entity
            crafting_system: Crafting system for recipe matching
            message_log: Message log for feedback
            entities: List of all entities (for dropping items if needed)
        """
        self.player = player
        self.crafting_system = crafting_system
        self.message_log = message_log
        self.entities = entities

    def execute(self) -> CommandResult:
        """Execute the auto craft command.

        Returns:
            CommandResult indicating success/failure
        """
        from roguelike.components.crafting import CraftingComponent

        # Check if player has inventory component
        inventory = self.player.get_component(InventoryComponent)
        if inventory is None:
            self.message_log.add_message("You have no inventory!")
            return CommandResult(success=False, turn_consumed=False)

        # Get all items with crafting components
        items = inventory.get_items()
        craftable_items = [
            item for item in items
            if item.get_component(CraftingComponent) is not None
        ]

        if len(craftable_items) < 2:
            self.message_log.add_message(
                "You need at least 2 craftable items!"
            )
            return CommandResult(success=False, turn_consumed=False)

        # Try all combinations of 2-3 items
        for size in [3, 2]:  # Try 3-item recipes first, then 2-item
            for combo in combinations(craftable_items, size):
                ingredients = list(combo)
                if self.crafting_system.can_craft(ingredients):
                    # Found a valid recipe - craft it
                    result, consumed = self.crafting_system.craft(
                        ingredients,
                        crafter=self.player,
                        position=self.player.position
                    )

                    if result is None:
                        continue  # Try next combination

                    # Remove consumed ingredients from inventory
                    for ingredient in consumed:
                        inventory.remove_item(ingredient)

                    # Add crafted item to inventory
                    if not inventory.add_item(result):
                        # Inventory full - drop at player's position
                        self.entities.append(result)
                        self.message_log.add_message(
                            f"Inventory full! {result.name} dropped on ground."
                        )

                    # Success - message already handled by event system
                    return CommandResult(success=True, turn_consumed=True)

        # No valid recipes found
        self.message_log.add_message(
            "No craftable recipes found with your current items."
        )
        return CommandResult(success=False, turn_consumed=False)


class StartCraftingCommand(Command):
    """Command to enter crafting mode and select ingredients.

    This command opens a crafting UI where players can select 2-3
    ingredients from their inventory to craft together.
    """

    def __init__(
        self,
        player: ComponentEntity,
        message_log: MessageLog,
    ):
        """Initialize start crafting command.

        Args:
            player: Player entity
            message_log: Message log for feedback
        """
        self.player = player
        self.message_log = message_log

    def execute(self) -> CommandResult:
        """Execute the start crafting command.

        Returns:
            CommandResult with data indicating crafting mode should start
        """
        # Check if player has inventory component
        inventory = self.player.get_component(InventoryComponent)
        if inventory is None:
            self.message_log.add_message("You have no inventory!")
            return CommandResult(success=False, turn_consumed=False)

        # Check if inventory has items
        items = inventory.get_items()
        if len(items) < 2:
            self.message_log.add_message(
                "You need at least 2 items to craft!"
            )
            return CommandResult(success=False, turn_consumed=False)

        # Signal to enter crafting mode
        self.message_log.add_message(
            "Select ingredients to craft (2-3 items). Press ESC to cancel."
        )
        return CommandResult(
            success=True,
            turn_consumed=False,
            data={"start_crafting": True}
        )
