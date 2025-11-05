"""Tests for recipe discovery component."""

import pytest

from roguelike.components.recipe_discovery import RecipeDiscoveryComponent
from roguelike.components.entity import ComponentEntity
from roguelike.utils.position import Position


def test_recipe_discovery_component_starts_empty():
    """Recipe discovery component starts with no discovered recipes."""
    component = RecipeDiscoveryComponent()
    assert len(component.get_discovered_recipes()) == 0


def test_recipe_discovery_component_get_discovery_count_starts_zero():
    """Discovery count starts at zero."""
    component = RecipeDiscoveryComponent()
    assert component.get_discovery_count() == 0


def test_is_discovered_returns_false_for_new_recipe():
    """is_discovered returns False for undiscovered recipe."""
    component = RecipeDiscoveryComponent()
    assert component.is_discovered("healing_potion") is False


def test_discover_recipe_returns_true_for_new_recipe():
    """discover_recipe returns True when discovering a new recipe."""
    component = RecipeDiscoveryComponent()
    result = component.discover_recipe("healing_potion")
    assert result is True


def test_discover_recipe_returns_false_for_already_discovered():
    """discover_recipe returns False for already discovered recipe."""
    component = RecipeDiscoveryComponent()
    component.discover_recipe("healing_potion")
    result = component.discover_recipe("healing_potion")
    assert result is False


def test_is_discovered_returns_true_after_discovery():
    """is_discovered returns True after recipe is discovered."""
    component = RecipeDiscoveryComponent()
    component.discover_recipe("healing_potion")
    assert component.is_discovered("healing_potion") is True


def test_get_discovered_recipes_contains_discovered_recipe():
    """get_discovered_recipes contains discovered recipe ID."""
    component = RecipeDiscoveryComponent()
    component.discover_recipe("healing_potion")
    recipes = component.get_discovered_recipes()
    assert "healing_potion" in recipes


def test_get_discovery_count_increments_on_discovery():
    """Discovery count increments when new recipe is discovered."""
    component = RecipeDiscoveryComponent()
    component.discover_recipe("healing_potion")
    assert component.get_discovery_count() == 1


def test_get_discovery_count_does_not_increment_on_rediscovery():
    """Discovery count does not increment on rediscovery."""
    component = RecipeDiscoveryComponent()
    component.discover_recipe("healing_potion")
    component.discover_recipe("healing_potion")
    assert component.get_discovery_count() == 1


def test_discover_multiple_recipes():
    """Multiple recipes can be discovered."""
    component = RecipeDiscoveryComponent()
    component.discover_recipe("healing_potion")
    component.discover_recipe("mana_potion")
    component.discover_recipe("strength_elixir")
    assert component.get_discovery_count() == 3


def test_get_discovered_recipes_contains_all_discovered():
    """get_discovered_recipes contains all discovered recipe IDs."""
    component = RecipeDiscoveryComponent()
    component.discover_recipe("healing_potion")
    component.discover_recipe("mana_potion")
    recipes = component.get_discovered_recipes()
    assert "healing_potion" in recipes
    assert "mana_potion" in recipes


def test_recipe_discovery_component_can_be_added_to_entity():
    """RecipeDiscoveryComponent can be added to ComponentEntity."""
    entity = ComponentEntity(
        position=Position(0, 0),
        char="@",
        name="Player",
    )
    component = RecipeDiscoveryComponent()
    entity.add_component(component)

    retrieved = entity.get_component(RecipeDiscoveryComponent)
    assert retrieved is component


def test_recipe_discovery_component_entity_reference():
    """RecipeDiscoveryComponent maintains reference to entity."""
    entity = ComponentEntity(
        position=Position(0, 0),
        char="@",
        name="Player",
    )
    component = RecipeDiscoveryComponent()
    entity.add_component(component)

    assert component.entity is entity


def test_get_discovered_recipes_returns_copy():
    """get_discovered_recipes returns a copy to prevent external modification."""
    component = RecipeDiscoveryComponent()
    component.discover_recipe("healing_potion")

    recipes = component.get_discovered_recipes()
    recipes.add("fake_recipe")

    # Original should not be modified
    assert "fake_recipe" not in component.get_discovered_recipes()
