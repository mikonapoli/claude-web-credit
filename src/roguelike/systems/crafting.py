"""Crafting system for recipe-based item creation."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, List, Optional, Set

if TYPE_CHECKING:
    from roguelike.components.entity import ComponentEntity
    from roguelike.data.recipe_loader import RecipeLoader
    from roguelike.engine.events import EventBus


@dataclass
class Recipe:
    """Represents a crafting recipe.

    Recipes define how to combine ingredients to create a result.
    Ingredients are matched by tags rather than specific items.
    """

    id: str
    name: str
    required_tags: List[Set[str]]
    result_type: str
    description: str

    def matches_ingredients(self, ingredient_tags: List[Set[str]]) -> bool:
        """Check if ingredients match this recipe.

        Args:
            ingredient_tags: List of tag sets, one per ingredient

        Returns:
            True if ingredients match recipe requirements
        """
        # Must have exact number of ingredients
        if len(ingredient_tags) != len(self.required_tags):
            return False

        # Try all permutations to match ingredients (order-independent)
        return self._matches_any_permutation(ingredient_tags, self.required_tags)

    def _matches_any_permutation(
        self, ingredient_tags: List[Set[str]], required_tags: List[Set[str]]
    ) -> bool:
        """Check if ingredients match required tags in any order.

        Args:
            ingredient_tags: List of tag sets from ingredients
            required_tags: List of required tag sets from recipe

        Returns:
            True if ingredients match in any permutation
        """
        if not required_tags:
            return True

        # Try matching first required tag set with each ingredient
        for i, ing_tags in enumerate(ingredient_tags):
            if required_tags[0].issubset(ing_tags):
                # Match found, recurse with remaining ingredients and requirements
                remaining_ingredients = ingredient_tags[:i] + ingredient_tags[i + 1 :]
                remaining_required = required_tags[1:]
                if self._matches_any_permutation(
                    remaining_ingredients, remaining_required
                ):
                    return True

        return False

    def __repr__(self) -> str:
        """Return string representation."""
        return f"Recipe(id={self.id!r}, name={self.name!r}, result={self.result_type!r})"


class CraftingSystem:
    """Manages crafting operations and recipe matching.

    This system handles crafting logic, finding matching recipes,
    and creating result items via the event bus.
    """

    def __init__(
        self,
        recipe_loader: "RecipeLoader",
        event_bus: Optional["EventBus"] = None,
    ):
        """Initialize crafting system.

        Args:
            recipe_loader: Loader for crafting recipes
            event_bus: Event bus for crafting events (optional)
        """
        self.recipe_loader = recipe_loader
        self.event_bus = event_bus

    def find_matching_recipe(
        self, ingredients: List["ComponentEntity"]
    ) -> Optional[Recipe]:
        """Find a recipe that matches the given ingredients.

        Args:
            ingredients: List of ingredient entities with CraftingComponents

        Returns:
            Matching recipe or None if no match found
        """
        from roguelike.components.crafting import CraftingComponent

        # Extract tags from ingredients
        ingredient_tags = []
        for ingredient in ingredients:
            crafting_comp = ingredient.get_component(CraftingComponent)
            if crafting_comp is None:
                return None  # All ingredients must have CraftingComponent
            ingredient_tags.append(crafting_comp.tags)

        # Check all recipes for a match
        for recipe in self.recipe_loader.get_all_recipes():
            if recipe.matches_ingredients(ingredient_tags):
                return recipe

        return None

    def can_craft(self, ingredients: List["ComponentEntity"]) -> bool:
        """Check if ingredients can be crafted into something.

        Args:
            ingredients: List of ingredient entities

        Returns:
            True if a matching recipe exists
        """
        return self.find_matching_recipe(ingredients) is not None

    def get_all_recipes(self) -> List[Recipe]:
        """Get all available recipes.

        Returns:
            List of all recipes
        """
        return self.recipe_loader.get_all_recipes()

    def get_recipe_by_id(self, recipe_id: str) -> Optional[Recipe]:
        """Get a specific recipe by ID.

        Args:
            recipe_id: Recipe identifier

        Returns:
            Recipe or None if not found
        """
        return self.recipe_loader.get_recipe(recipe_id)

    def craft(
        self,
        ingredients: List["ComponentEntity"],
        crafter: Optional["ComponentEntity"] = None,
        position: Optional["Position"] = None,
    ) -> tuple[Optional["ComponentEntity"], List["ComponentEntity"]]:
        """Attempt to craft items together.

        Args:
            ingredients: List of ingredient entities to combine
            crafter: Entity performing the crafting (for events and position)
            position: Explicit position for crafted item (overrides crafter position)

        Returns:
            Tuple of (result_item, consumed_ingredients)
            - result_item: Crafted item entity or None if crafting failed
            - consumed_ingredients: List of ingredients that should be removed/destroyed

            Caller is responsible for removing consumed ingredients from inventory/map.

        Note:
            Position priority: explicit position > crafter position > fail
            Ingredients that have been picked up retain their map coordinates,
            so we must use crafter's current position, not ingredient positions.

            Ingredients marked as consumable in their CraftingComponent will be
            included in the consumed list. Non-consumable ingredients (tools) are
            not consumed and can be reused.
        """
        from roguelike.components.crafting import CraftingComponent
        from roguelike.data.entity_loader import EntityLoader
        from roguelike.engine.events import CraftingAttemptEvent
        from roguelike.utils.position import Position

        # Find matching recipe
        recipe = self.find_matching_recipe(ingredients)

        crafter_name = crafter.name if crafter else "Unknown"
        ingredient_names = [ing.name for ing in ingredients]

        if recipe is None:
            # Crafting failed - no matching recipe
            if self.event_bus:
                event = CraftingAttemptEvent(
                    crafter_name=crafter_name,
                    ingredient_names=ingredient_names,
                    success=False,
                    result_name=None,
                )
                self.event_bus.emit(event)
            return None, []

        # Determine spawn position for crafted item
        # Priority: explicit position > crafter position > None
        spawn_position = position
        if spawn_position is None and crafter is not None:
            spawn_position = crafter.position

        if spawn_position is None:
            # Cannot craft without a position
            return None, []

        # Determine which ingredients are consumable
        consumed_ingredients = []
        for ingredient in ingredients:
            crafting_comp = ingredient.get_component(CraftingComponent)
            if crafting_comp and crafting_comp.consumable:
                consumed_ingredients.append(ingredient)

        # Load the result entity
        entity_loader = EntityLoader()
        result = entity_loader.create_entity(recipe.result_type, spawn_position)

        # Handle recipe discovery
        if crafter is not None:
            from roguelike.components.recipe_discovery import RecipeDiscoveryComponent
            from roguelike.engine.events import RecipeDiscoveredEvent

            discovery_comp = crafter.get_component(RecipeDiscoveryComponent)
            if discovery_comp is not None:
                # Try to discover the recipe
                newly_discovered = discovery_comp.discover_recipe(recipe.id)
                if newly_discovered and self.event_bus:
                    # Emit recipe discovered event
                    discovery_event = RecipeDiscoveredEvent(
                        recipe_id=recipe.id,
                        recipe_name=recipe.name,
                        discoverer_name=crafter_name,
                    )
                    self.event_bus.emit(discovery_event)

        # Emit success event
        if self.event_bus:
            event = CraftingAttemptEvent(
                crafter_name=crafter_name,
                ingredient_names=ingredient_names,
                success=True,
                result_name=result.name,
            )
            self.event_bus.emit(event)

        return result, consumed_ingredients
