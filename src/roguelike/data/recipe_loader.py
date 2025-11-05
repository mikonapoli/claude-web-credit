"""Recipe loader for data-driven crafting recipes."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from roguelike.systems.crafting import Recipe


class RecipeLoader:
    """Loads crafting recipe definitions from JSON files."""

    def __init__(self, data_path: Path | str | None = None):
        """Initialize recipe loader.

        Args:
            data_path: Path to recipes.json file. If None, uses default.
        """
        if data_path is None:
            # Default to recipes.json in same directory as this file
            data_path = Path(__file__).parent / "recipes.json"
        else:
            data_path = Path(data_path)

        self.data_path = data_path
        self.recipes: Dict[str, Recipe] = {}
        self._load_recipes()

    def _load_recipes(self) -> None:
        """Load recipes from JSON file."""
        with open(self.data_path, "r") as f:
            data = json.load(f)

        for recipe_id, recipe_data in data.items():
            self.recipes[recipe_id] = self._parse_recipe(recipe_id, recipe_data)

    def _parse_recipe(self, recipe_id: str, data: Dict[str, Any]) -> Recipe:
        """Parse a recipe from JSON data.

        Args:
            recipe_id: Recipe identifier
            data: Recipe data from JSON

        Returns:
            Recipe instance
        """
        # Convert list of lists to list of sets
        required_tags = [set(tag_list) for tag_list in data["required_tags"]]

        return Recipe(
            id=recipe_id,
            name=data["name"],
            required_tags=required_tags,
            result_type=data["result_type"],
            description=data["description"],
        )

    def get_recipe(self, recipe_id: str) -> Optional[Recipe]:
        """Get a recipe by ID.

        Args:
            recipe_id: Recipe identifier

        Returns:
            Recipe or None if not found
        """
        return self.recipes.get(recipe_id)

    def get_all_recipes(self) -> List[Recipe]:
        """Get all loaded recipes.

        Returns:
            List of all recipes
        """
        return list(self.recipes.values())

    def get_recipe_ids(self) -> List[str]:
        """Get list of all recipe IDs.

        Returns:
            List of recipe identifiers
        """
        return list(self.recipes.keys())

    def reload(self) -> None:
        """Reload recipes from JSON file."""
        self.recipes.clear()
        self._load_recipes()
