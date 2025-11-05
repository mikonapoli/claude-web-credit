"""Recipe discovery component for tracking discovered recipes."""

from typing import Set

from roguelike.components.component import Component


class RecipeDiscoveryComponent(Component):
    """Component that tracks which recipes an entity has discovered.

    Recipes are discovered when successfully crafted, allowing the game
    to provide feedback about new discoveries and potentially unlock
    recipe hints or crafting assistance.
    """

    def __init__(self):
        """Initialize recipe discovery component."""
        super().__init__()
        self._discovered_recipes: Set[str] = set()

    def discover_recipe(self, recipe_id: str) -> bool:
        """Mark a recipe as discovered.

        Args:
            recipe_id: ID of the recipe to discover

        Returns:
            True if recipe was newly discovered, False if already known
        """
        if recipe_id in self._discovered_recipes:
            return False

        self._discovered_recipes.add(recipe_id)
        return True

    def is_discovered(self, recipe_id: str) -> bool:
        """Check if a recipe has been discovered.

        Args:
            recipe_id: ID of the recipe to check

        Returns:
            True if recipe has been discovered
        """
        return recipe_id in self._discovered_recipes

    def get_discovered_recipes(self) -> Set[str]:
        """Get all discovered recipe IDs.

        Returns:
            Copy of the set of discovered recipe IDs
        """
        return self._discovered_recipes.copy()

    def get_discovery_count(self) -> int:
        """Get the number of discovered recipes.

        Returns:
            Count of discovered recipes
        """
        return len(self._discovered_recipes)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"RecipeDiscoveryComponent(discovered={len(self._discovered_recipes)})"
