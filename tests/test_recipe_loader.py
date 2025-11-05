"""Tests for recipe loader."""

import json
import tempfile
from pathlib import Path

import pytest

from roguelike.data.recipe_loader import RecipeLoader


def test_recipe_loader_loads_default_recipes():
    """RecipeLoader loads recipes from default path."""
    loader = RecipeLoader()
    recipes = loader.get_all_recipes()
    assert len(recipes) > 0


def test_recipe_loader_can_get_recipe_by_id():
    """RecipeLoader can retrieve recipe by ID."""
    loader = RecipeLoader()
    recipe = loader.get_recipe("healing_potion")
    assert recipe is not None
    assert recipe.name == "Healing Potion"


def test_recipe_loader_returns_none_for_missing_recipe():
    """RecipeLoader returns None for non-existent recipe."""
    loader = RecipeLoader()
    recipe = loader.get_recipe("nonexistent_recipe")
    assert recipe is None


def test_recipe_loader_gets_all_recipe_ids():
    """RecipeLoader returns list of all recipe IDs."""
    loader = RecipeLoader()
    recipe_ids = loader.get_recipe_ids()
    assert "healing_potion" in recipe_ids


def test_recipe_loader_parses_required_tags_correctly():
    """RecipeLoader correctly parses required tags as sets."""
    loader = RecipeLoader()
    recipe = loader.get_recipe("healing_potion")
    assert recipe is not None
    assert len(recipe.required_tags) == 2
    assert {"herbal"} in recipe.required_tags
    assert {"magical"} in recipe.required_tags


def test_recipe_loader_loads_custom_path():
    """RecipeLoader can load recipes from custom path."""
    # Create temporary recipe file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(
            {
                "test_recipe": {
                    "name": "Test Recipe",
                    "required_tags": [["tag1"], ["tag2"]],
                    "result_type": "test_result",
                    "description": "Test description",
                }
            },
            f,
        )
        temp_path = f.name

    try:
        loader = RecipeLoader(data_path=temp_path)
        recipe = loader.get_recipe("test_recipe")
        assert recipe is not None
        assert recipe.name == "Test Recipe"
    finally:
        Path(temp_path).unlink()


def test_recipe_loader_parses_multi_tag_requirements():
    """RecipeLoader correctly parses ingredients with multiple required tags."""
    # Create temporary recipe with multi-tag requirement
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(
            {
                "complex_recipe": {
                    "name": "Complex Recipe",
                    "required_tags": [["herbal", "magical"], ["rare"]],
                    "result_type": "complex_result",
                    "description": "Complex description",
                }
            },
            f,
        )
        temp_path = f.name

    try:
        loader = RecipeLoader(data_path=temp_path)
        recipe = loader.get_recipe("complex_recipe")
        assert recipe is not None
        assert {"herbal", "magical"} in recipe.required_tags
        assert {"rare"} in recipe.required_tags
    finally:
        Path(temp_path).unlink()


def test_recipe_loader_reload_refreshes_recipes():
    """RecipeLoader reload() refreshes recipe data."""
    # Create initial recipe file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as f:
        json.dump(
            {
                "initial_recipe": {
                    "name": "Initial",
                    "required_tags": [["tag1"]],
                    "result_type": "initial",
                    "description": "Initial",
                }
            },
            f,
        )
        temp_path = f.name

    try:
        loader = RecipeLoader(data_path=temp_path)
        assert loader.get_recipe("initial_recipe") is not None

        # Update file with new recipe
        with open(temp_path, "w") as f:
            json.dump(
                {
                    "updated_recipe": {
                        "name": "Updated",
                        "required_tags": [["tag1"]],
                        "result_type": "updated",
                        "description": "Updated",
                    }
                },
                f,
            )

        # Reload and verify
        loader.reload()
        assert loader.get_recipe("initial_recipe") is None
        assert loader.get_recipe("updated_recipe") is not None
    finally:
        Path(temp_path).unlink()
