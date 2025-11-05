"""Tests for crafting recipes."""

import pytest

from roguelike.systems.crafting import Recipe


def test_recipe_creation():
    """Recipe can be created with required fields."""
    recipe = Recipe(
        id="healing_potion",
        name="Healing Potion",
        required_tags=[{"herbal"}, {"magical"}],
        result_type="healing_potion",
        description="Combines herbs and magic to heal wounds",
    )
    assert recipe.id == "healing_potion"
    assert recipe.name == "Healing Potion"
    assert len(recipe.required_tags) == 2


def test_recipe_matches_exact_tags():
    """Recipe matches ingredients with exact tags."""
    recipe = Recipe(
        id="test",
        name="Test",
        required_tags=[{"herbal"}, {"magical"}],
        result_type="potion",
        description="Test recipe",
    )
    ingredient_tags = [{"herbal"}, {"magical"}]
    assert recipe.matches_ingredients(ingredient_tags) is True


def test_recipe_matches_ingredients_with_extra_tags():
    """Recipe matches ingredients that have extra tags."""
    recipe = Recipe(
        id="test",
        name="Test",
        required_tags=[{"herbal"}, {"magical"}],
        result_type="potion",
        description="Test recipe",
    )
    # Ingredients have required tags plus extra ones
    ingredient_tags = [{"herbal", "rare"}, {"magical", "powerful"}]
    assert recipe.matches_ingredients(ingredient_tags) is True


def test_recipe_matches_regardless_of_order():
    """Recipe matches ingredients in any order."""
    recipe = Recipe(
        id="test",
        name="Test",
        required_tags=[{"herbal"}, {"magical"}],
        result_type="potion",
        description="Test recipe",
    )
    # Ingredients in different order than recipe
    ingredient_tags = [{"magical"}, {"herbal"}]
    assert recipe.matches_ingredients(ingredient_tags) is True


def test_recipe_does_not_match_missing_tags():
    """Recipe does not match when ingredients lack required tags."""
    recipe = Recipe(
        id="test",
        name="Test",
        required_tags=[{"herbal"}, {"magical"}],
        result_type="potion",
        description="Test recipe",
    )
    ingredient_tags = [{"herbal"}, {"metallic"}]  # Missing magical
    assert recipe.matches_ingredients(ingredient_tags) is False


def test_recipe_does_not_match_wrong_number_of_ingredients():
    """Recipe does not match with wrong ingredient count."""
    recipe = Recipe(
        id="test",
        name="Test",
        required_tags=[{"herbal"}, {"magical"}],
        result_type="potion",
        description="Test recipe",
    )
    ingredient_tags = [{"herbal"}]  # Only one ingredient
    assert recipe.matches_ingredients(ingredient_tags) is False


def test_recipe_matches_three_ingredients():
    """Recipe can match three ingredients."""
    recipe = Recipe(
        id="test",
        name="Test",
        required_tags=[{"herbal"}, {"magical"}, {"rare"}],
        result_type="potion",
        description="Test recipe",
    )
    ingredient_tags = [{"herbal"}, {"magical"}, {"rare"}]
    assert recipe.matches_ingredients(ingredient_tags) is True


def test_recipe_matches_three_ingredients_any_order():
    """Recipe matches three ingredients in any order."""
    recipe = Recipe(
        id="test",
        name="Test",
        required_tags=[{"herbal"}, {"magical"}, {"rare"}],
        result_type="potion",
        description="Test recipe",
    )
    ingredient_tags = [{"rare"}, {"herbal"}, {"magical"}]
    assert recipe.matches_ingredients(ingredient_tags) is True


def test_recipe_matches_multiple_required_tags_per_ingredient():
    """Recipe matches ingredients that need multiple tags."""
    recipe = Recipe(
        id="test",
        name="Test",
        required_tags=[{"herbal", "magical"}, {"rare"}],
        result_type="potion",
        description="Test recipe",
    )
    ingredient_tags = [{"herbal", "magical", "extra"}, {"rare"}]
    assert recipe.matches_ingredients(ingredient_tags) is True


def test_recipe_does_not_match_partial_required_tags():
    """Recipe does not match if ingredient lacks one of multiple required tags."""
    recipe = Recipe(
        id="test",
        name="Test",
        required_tags=[{"herbal", "magical"}, {"rare"}],
        result_type="potion",
        description="Test recipe",
    )
    ingredient_tags = [{"herbal"}, {"rare"}]  # Missing magical
    assert recipe.matches_ingredients(ingredient_tags) is False
