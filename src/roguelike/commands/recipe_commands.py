"""Recipe discovery related commands."""

from typing import List

from roguelike.commands.command import Command, CommandResult
from roguelike.components.entity import ComponentEntity
from roguelike.components.recipe_discovery import RecipeDiscoveryComponent
from roguelike.systems.crafting import CraftingSystem
from roguelike.ui.message_log import MessageLog


class ShowRecipeBookCommand(Command):
    """Command to display the recipe book showing discovered/undiscovered recipes."""

    def __init__(
        self,
        player: ComponentEntity,
        crafting_system: CraftingSystem,
        message_log: MessageLog,
    ):
        """Initialize show recipe book command.

        Args:
            player: Player entity
            crafting_system: Crafting system for accessing recipes
            message_log: Message log for feedback
        """
        self.player = player
        self.crafting_system = crafting_system
        self.message_log = message_log

    def execute(self) -> CommandResult:
        """Execute the show recipe book command.

        Returns:
            CommandResult with data to signal recipe book display
        """
        # Check if player has recipe discovery component
        discovery = self.player.get_component(RecipeDiscoveryComponent)
        if discovery is None:
            self.message_log.add_message("You have no recipe book!")
            return CommandResult(success=False, turn_consumed=False)

        # Get all recipes and discovered recipes
        all_recipes = self.crafting_system.get_all_recipes()
        discovered_recipe_ids = discovery.get_discovered_recipes()

        # Build recipe list with discovery status
        recipes_data = []
        for recipe in all_recipes:
            is_discovered = recipe.id in discovered_recipe_ids
            recipes_data.append({
                "recipe": recipe,
                "discovered": is_discovered,
            })

        # Signal to display recipe book UI
        return CommandResult(
            success=True,
            turn_consumed=False,
            data={
                "show_recipe_book": True,
                "recipes": recipes_data,
            }
        )
