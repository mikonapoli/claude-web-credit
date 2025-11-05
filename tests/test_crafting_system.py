"""Tests for crafting system."""

import json
import tempfile
from pathlib import Path

import pytest

from roguelike.components.crafting import CraftingComponent
from roguelike.components.entity import ComponentEntity
from roguelike.data.recipe_loader import RecipeLoader
from roguelike.systems.crafting import CraftingSystem
from roguelike.utils.position import Position


@pytest.fixture
def recipe_loader():
    """Create a recipe loader with test recipes."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(
            {
                "test_potion": {
                    "name": "Test Potion",
                    "required_tags": [["herbal"], ["magical"]],
                    "result_type": "test_potion",
                    "description": "Test potion description",
                },
                "test_elixir": {
                    "name": "Test Elixir",
                    "required_tags": [["herbal"], ["magical"], ["rare"]],
                    "result_type": "test_elixir",
                    "description": "Test elixir description",
                },
            },
            f,
        )
        temp_path = f.name

    loader = RecipeLoader(data_path=temp_path)
    yield loader
    Path(temp_path).unlink()


@pytest.fixture
def crafting_system(recipe_loader):
    """Create a crafting system with test recipes."""
    return CraftingSystem(recipe_loader=recipe_loader)


def test_crafting_system_creation(recipe_loader):
    """CraftingSystem can be created with recipe loader."""
    system = CraftingSystem(recipe_loader=recipe_loader)
    assert system.recipe_loader is recipe_loader


def test_crafting_system_finds_matching_recipe(crafting_system):
    """CraftingSystem finds recipe that matches ingredients."""
    # Create ingredients with matching tags
    herb = ComponentEntity(position=Position(0, 0), char="h", name="Herb")
    herb.add_component(CraftingComponent(tags={"herbal"}))

    crystal = ComponentEntity(position=Position(0, 0), char="c", name="Crystal")
    crystal.add_component(CraftingComponent(tags={"magical"}))

    recipe = crafting_system.find_matching_recipe([herb, crystal])
    assert recipe is not None
    assert recipe.id == "test_potion"


def test_crafting_system_finds_recipe_regardless_of_order(crafting_system):
    """CraftingSystem finds recipe regardless of ingredient order."""
    herb = ComponentEntity(position=Position(0, 0), char="h", name="Herb")
    herb.add_component(CraftingComponent(tags={"herbal"}))

    crystal = ComponentEntity(position=Position(0, 0), char="c", name="Crystal")
    crystal.add_component(CraftingComponent(tags={"magical"}))

    # Try in different order
    recipe = crafting_system.find_matching_recipe([crystal, herb])
    assert recipe is not None
    assert recipe.id == "test_potion"


def test_crafting_system_returns_none_for_no_match(crafting_system):
    """CraftingSystem returns None when no recipe matches."""
    herb = ComponentEntity(position=Position(0, 0), char="h", name="Herb")
    herb.add_component(CraftingComponent(tags={"herbal"}))

    metal = ComponentEntity(position=Position(0, 0), char="m", name="Metal")
    metal.add_component(CraftingComponent(tags={"metallic"}))

    recipe = crafting_system.find_matching_recipe([herb, metal])
    assert recipe is None


def test_crafting_system_returns_none_for_non_craftable_items(crafting_system):
    """CraftingSystem returns None for items without CraftingComponent."""
    item1 = ComponentEntity(position=Position(0, 0), char="i", name="Item1")
    item2 = ComponentEntity(position=Position(0, 0), char="i", name="Item2")

    recipe = crafting_system.find_matching_recipe([item1, item2])
    assert recipe is None


def test_crafting_system_can_craft_returns_true_for_valid_ingredients(crafting_system):
    """CraftingSystem can_craft returns True for valid ingredients."""
    herb = ComponentEntity(position=Position(0, 0), char="h", name="Herb")
    herb.add_component(CraftingComponent(tags={"herbal"}))

    crystal = ComponentEntity(position=Position(0, 0), char="c", name="Crystal")
    crystal.add_component(CraftingComponent(tags={"magical"}))

    assert crafting_system.can_craft([herb, crystal]) is True


def test_crafting_system_can_craft_returns_false_for_invalid_ingredients(
    crafting_system,
):
    """CraftingSystem can_craft returns False for invalid ingredients."""
    herb = ComponentEntity(position=Position(0, 0), char="h", name="Herb")
    herb.add_component(CraftingComponent(tags={"herbal"}))

    metal = ComponentEntity(position=Position(0, 0), char="m", name="Metal")
    metal.add_component(CraftingComponent(tags={"metallic"}))

    assert crafting_system.can_craft([herb, metal]) is False


def test_crafting_system_finds_recipe_with_three_ingredients(crafting_system):
    """CraftingSystem finds recipe requiring three ingredients."""
    herb = ComponentEntity(position=Position(0, 0), char="h", name="Herb")
    herb.add_component(CraftingComponent(tags={"herbal"}))

    crystal = ComponentEntity(position=Position(0, 0), char="c", name="Crystal")
    crystal.add_component(CraftingComponent(tags={"magical"}))

    gem = ComponentEntity(position=Position(0, 0), char="g", name="Gem")
    gem.add_component(CraftingComponent(tags={"rare"}))

    recipe = crafting_system.find_matching_recipe([herb, crystal, gem])
    assert recipe is not None
    assert recipe.id == "test_elixir"


def test_crafting_system_gets_all_recipes(crafting_system):
    """CraftingSystem can retrieve all recipes."""
    recipes = crafting_system.get_all_recipes()
    assert len(recipes) == 2
    recipe_ids = [r.id for r in recipes]
    assert "test_potion" in recipe_ids
    assert "test_elixir" in recipe_ids


def test_crafting_system_gets_recipe_by_id(crafting_system):
    """CraftingSystem can retrieve recipe by ID."""
    recipe = crafting_system.get_recipe_by_id("test_potion")
    assert recipe is not None
    assert recipe.name == "Test Potion"


def test_crafting_system_matches_ingredients_with_extra_tags(crafting_system):
    """CraftingSystem matches ingredients that have more tags than required."""
    herb = ComponentEntity(position=Position(0, 0), char="h", name="Rare Herb")
    herb.add_component(CraftingComponent(tags={"herbal", "rare", "verdant"}))

    crystal = ComponentEntity(position=Position(0, 0), char="c", name="Power Crystal")
    crystal.add_component(CraftingComponent(tags={"magical", "powerful"}))

    recipe = crafting_system.find_matching_recipe([herb, crystal])
    assert recipe is not None
    assert recipe.id == "test_potion"


def test_crafting_system_craft_creates_result():
    """CraftingSystem craft() creates result item."""
    # Use actual recipe loader for this test
    from roguelike.data.entity_loader import EntityLoader
    from roguelike.data.recipe_loader import RecipeLoader
    from roguelike.systems.crafting import CraftingSystem

    recipe_loader = RecipeLoader()
    crafting_system = CraftingSystem(recipe_loader=recipe_loader)
    entity_loader = EntityLoader()

    # Create ingredients
    moonleaf = entity_loader.create_entity("moonleaf", Position(5, 5))
    crystal = entity_loader.create_entity("mana_crystal", Position(5, 5))

    # Craft with explicit position
    result = crafting_system.craft([moonleaf, crystal], position=Position(5, 5))

    assert result is not None
    assert result.name == "Healing Potion"


def test_crafting_system_craft_returns_none_for_no_match():
    """CraftingSystem craft() returns None when no recipe matches."""
    from roguelike.data.entity_loader import EntityLoader
    from roguelike.data.recipe_loader import RecipeLoader
    from roguelike.systems.crafting import CraftingSystem

    recipe_loader = RecipeLoader()
    crafting_system = CraftingSystem(recipe_loader=recipe_loader)
    entity_loader = EntityLoader()

    # Create ingredients that don't match any recipe
    moonleaf = entity_loader.create_entity("moonleaf", Position(5, 5))
    iron = entity_loader.create_entity("iron_ore", Position(5, 5))

    # Craft
    result = crafting_system.craft([moonleaf, iron])

    assert result is None


def test_crafting_system_craft_emits_success_event():
    """CraftingSystem craft() emits success event."""
    from roguelike.data.entity_loader import EntityLoader
    from roguelike.data.recipe_loader import RecipeLoader
    from roguelike.engine.events import EventBus
    from roguelike.systems.crafting import CraftingSystem

    recipe_loader = RecipeLoader()
    event_bus = EventBus()
    crafting_system = CraftingSystem(recipe_loader=recipe_loader, event_bus=event_bus)
    entity_loader = EntityLoader()

    received_events = []

    def handler(event):
        received_events.append(event)

    event_bus.subscribe("crafting_attempt", handler)

    # Create ingredients
    moonleaf = entity_loader.create_entity("moonleaf", Position(5, 5))
    crystal = entity_loader.create_entity("mana_crystal", Position(5, 5))

    # Craft with explicit position
    result = crafting_system.craft([moonleaf, crystal], position=Position(5, 5))

    assert len(received_events) == 1
    assert received_events[0].success is True
    assert received_events[0].result_name == "Healing Potion"


def test_crafting_system_craft_emits_failure_event():
    """CraftingSystem craft() emits failure event."""
    from roguelike.data.entity_loader import EntityLoader
    from roguelike.data.recipe_loader import RecipeLoader
    from roguelike.engine.events import EventBus
    from roguelike.systems.crafting import CraftingSystem

    recipe_loader = RecipeLoader()
    event_bus = EventBus()
    crafting_system = CraftingSystem(recipe_loader=recipe_loader, event_bus=event_bus)
    entity_loader = EntityLoader()

    received_events = []

    def handler(event):
        received_events.append(event)

    event_bus.subscribe("crafting_attempt", handler)

    # Create ingredients that don't match
    moonleaf = entity_loader.create_entity("moonleaf", Position(5, 5))
    iron = entity_loader.create_entity("iron_ore", Position(5, 5))

    # Craft
    result = crafting_system.craft([moonleaf, iron])

    assert len(received_events) == 1
    assert received_events[0].success is False
    assert received_events[0].result_name is None


def test_crafting_system_craft_with_crafter():
    """CraftingSystem craft() includes crafter name in event."""
    from roguelike.data.entity_loader import EntityLoader
    from roguelike.data.recipe_loader import RecipeLoader
    from roguelike.engine.events import EventBus
    from roguelike.systems.crafting import CraftingSystem

    recipe_loader = RecipeLoader()
    event_bus = EventBus()
    crafting_system = CraftingSystem(recipe_loader=recipe_loader, event_bus=event_bus)
    entity_loader = EntityLoader()

    received_events = []

    def handler(event):
        received_events.append(event)

    event_bus.subscribe("crafting_attempt", handler)

    # Create player as crafter
    player = entity_loader.create_entity("player", Position(0, 0))

    # Create ingredients
    moonleaf = entity_loader.create_entity("moonleaf", Position(5, 5))
    crystal = entity_loader.create_entity("mana_crystal", Position(5, 5))

    # Craft
    result = crafting_system.craft([moonleaf, crystal], crafter=player)

    assert len(received_events) == 1
    assert received_events[0].crafter_name == "Player"


def test_crafting_uses_crafter_position():
    """Crafted item spawns at crafter's position, not ingredient position."""
    from roguelike.data.entity_loader import EntityLoader
    from roguelike.data.recipe_loader import RecipeLoader
    from roguelike.systems.crafting import CraftingSystem
    from roguelike.utils.position import Position

    recipe_loader = RecipeLoader()
    crafting_system = CraftingSystem(recipe_loader=recipe_loader)
    entity_loader = EntityLoader()

    # Create player at position (10, 10)
    player = entity_loader.create_entity("player", Position(10, 10))

    # Create ingredients at different positions (simulating picked up items)
    moonleaf = entity_loader.create_entity("moonleaf", Position(1, 1))
    crystal = entity_loader.create_entity("mana_crystal", Position(2, 2))

    # Craft - result should spawn at player position (10, 10)
    result = crafting_system.craft([moonleaf, crystal], crafter=player)

    assert result is not None
    assert result.position == Position(10, 10)  # Crafter's position
    assert result.position != Position(1, 1)  # Not first ingredient's position


def test_crafting_with_explicit_position():
    """Explicit position parameter overrides crafter position."""
    from roguelike.data.entity_loader import EntityLoader
    from roguelike.data.recipe_loader import RecipeLoader
    from roguelike.systems.crafting import CraftingSystem
    from roguelike.utils.position import Position

    recipe_loader = RecipeLoader()
    crafting_system = CraftingSystem(recipe_loader=recipe_loader)
    entity_loader = EntityLoader()

    # Create player at position (10, 10)
    player = entity_loader.create_entity("player", Position(10, 10))

    # Create ingredients
    moonleaf = entity_loader.create_entity("moonleaf", Position(1, 1))
    crystal = entity_loader.create_entity("mana_crystal", Position(2, 2))

    # Craft with explicit position (15, 15)
    target_pos = Position(15, 15)
    result = crafting_system.craft([moonleaf, crystal], crafter=player, position=target_pos)

    assert result is not None
    assert result.position == Position(15, 15)  # Explicit position
    assert result.position != Position(10, 10)  # Not crafter's position


def test_crafting_without_crafter_or_position_fails():
    """Crafting without crafter or explicit position returns None."""
    from roguelike.data.entity_loader import EntityLoader
    from roguelike.data.recipe_loader import RecipeLoader
    from roguelike.systems.crafting import CraftingSystem
    from roguelike.utils.position import Position

    recipe_loader = RecipeLoader()
    crafting_system = CraftingSystem(recipe_loader=recipe_loader)
    entity_loader = EntityLoader()

    # Create ingredients (no crafter provided)
    moonleaf = entity_loader.create_entity("moonleaf", Position(1, 1))
    crystal = entity_loader.create_entity("mana_crystal", Position(2, 2))

    # Craft without crafter or position - should fail
    result = crafting_system.craft([moonleaf, crystal])

    assert result is None


def test_crafting_with_only_position_succeeds():
    """Crafting with only explicit position (no crafter) succeeds."""
    from roguelike.data.entity_loader import EntityLoader
    from roguelike.data.recipe_loader import RecipeLoader
    from roguelike.systems.crafting import CraftingSystem
    from roguelike.utils.position import Position

    recipe_loader = RecipeLoader()
    crafting_system = CraftingSystem(recipe_loader=recipe_loader)
    entity_loader = EntityLoader()

    # Create ingredients
    moonleaf = entity_loader.create_entity("moonleaf", Position(1, 1))
    crystal = entity_loader.create_entity("mana_crystal", Position(2, 2))

    # Craft with explicit position but no crafter
    target_pos = Position(20, 20)
    result = crafting_system.craft([moonleaf, crystal], position=target_pos)

    assert result is not None
    assert result.position == Position(20, 20)
