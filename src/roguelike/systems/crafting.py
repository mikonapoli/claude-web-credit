"""Crafting system for recipe-based item creation."""

from dataclasses import dataclass
from typing import List, Optional, Set


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
