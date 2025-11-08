"""Tests for recipe discovery commands."""

import pytest

from roguelike.commands.recipe_commands import ShowRecipeBookCommand
from roguelike.components.entity import ComponentEntity
from roguelike.components.recipe_discovery import RecipeDiscoveryComponent
from roguelike.data.recipe_loader import RecipeLoader
from roguelike.engine.events import EventBus
from roguelike.systems.crafting import CraftingSystem
from roguelike.ui.message_log import MessageLog
from roguelike.utils.position import Position


@pytest.fixture
def event_bus():
    """Create event bus for testing."""
    return EventBus()


@pytest.fixture
def recipe_loader():
    """Create recipe loader for testing."""
    return RecipeLoader()


@pytest.fixture
def crafting_system(recipe_loader, event_bus):
    """Create crafting system for testing."""
    return CraftingSystem(recipe_loader, event_bus)


@pytest.fixture
def message_log():
    """Create message log for testing."""
    return MessageLog()


@pytest.fixture
def player():
    """Create player entity with recipe discovery component for testing."""
    player = ComponentEntity(
        position=Position(10, 10),
        char="@",
        name="Player",
        blocks_movement=True,
    )
    player.add_component(RecipeDiscoveryComponent())
    return player


def test_show_recipe_book_command_succeeds_with_component(player, crafting_system, message_log):
    """ShowRecipeBookCommand succeeds when player has RecipeDiscoveryComponent."""
    command = ShowRecipeBookCommand(player, crafting_system, message_log)
    result = command.execute()

    assert result.success is True
    assert result.turn_consumed is False
    assert result.data is not None
    assert result.data.get("show_recipe_book") is True
    assert "recipes" in result.data


def test_show_recipe_book_command_returns_all_recipes(player, crafting_system, message_log):
    """ShowRecipeBookCommand returns all available recipes."""
    command = ShowRecipeBookCommand(player, crafting_system, message_log)
    result = command.execute()

    recipes_data = result.data.get("recipes", [])
    all_recipes = crafting_system.get_all_recipes()

    # Should return data for all recipes
    assert len(recipes_data) == len(all_recipes)


def test_show_recipe_book_command_shows_discovered_status(player, crafting_system, message_log):
    """ShowRecipeBookCommand shows correct discovered status for recipes."""
    # Discover one recipe
    discovery = player.get_component(RecipeDiscoveryComponent)
    discovery.discover_recipe("healing_potion")

    command = ShowRecipeBookCommand(player, crafting_system, message_log)
    result = command.execute()

    recipes_data = result.data.get("recipes", [])

    # Find the healing potion recipe
    healing_potion_data = next(
        (r for r in recipes_data if r["recipe"].id == "healing_potion"),
        None
    )

    assert healing_potion_data is not None
    assert healing_potion_data["discovered"] is True

    # Check that other recipes are not discovered
    other_recipe = next(
        (r for r in recipes_data if r["recipe"].id != "healing_potion"),
        None
    )
    assert other_recipe is not None
    assert other_recipe["discovered"] is False


def test_show_recipe_book_command_fails_without_component(crafting_system, message_log):
    """ShowRecipeBookCommand fails when player lacks RecipeDiscoveryComponent."""
    player_without_component = ComponentEntity(
        position=Position(10, 10),
        char="@",
        name="Player",
        blocks_movement=True,
    )

    command = ShowRecipeBookCommand(player_without_component, crafting_system, message_log)
    result = command.execute()

    assert result.success is False
    assert result.turn_consumed is False
    assert "no recipe book" in message_log.get_messages(1)[0].lower()


def test_show_recipe_book_command_does_not_consume_turn(player, crafting_system, message_log):
    """ShowRecipeBookCommand does not consume a turn."""
    command = ShowRecipeBookCommand(player, crafting_system, message_log)
    result = command.execute()

    assert result.turn_consumed is False
