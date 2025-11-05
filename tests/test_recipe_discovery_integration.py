"""Tests for recipe discovery integration with crafting system."""

import pytest

from roguelike.components.entity import ComponentEntity
from roguelike.components.recipe_discovery import RecipeDiscoveryComponent
from roguelike.data.entity_loader import EntityLoader
from roguelike.data.recipe_loader import RecipeLoader
from roguelike.engine.events import EventBus
from roguelike.systems.crafting import CraftingSystem
from roguelike.utils.position import Position


@pytest.fixture
def crafter_with_discovery():
    """Create a crafter entity with RecipeDiscoveryComponent."""
    entity = ComponentEntity(
        position=Position(5, 5),
        char="@",
        name="Player",
    )
    entity.add_component(RecipeDiscoveryComponent())
    return entity


@pytest.fixture
def crafter_without_discovery():
    """Create a crafter entity without RecipeDiscoveryComponent."""
    entity = ComponentEntity(
        position=Position(5, 5),
        char="@",
        name="Player",
    )
    return entity


def test_craft_discovers_recipe_on_first_success(crafter_with_discovery):
    """Crafting successfully discovers recipe on first craft."""
    recipe_loader = RecipeLoader()
    event_bus = EventBus()
    crafting_system = CraftingSystem(recipe_loader=recipe_loader, event_bus=event_bus)
    entity_loader = EntityLoader()

    # Get discovery component
    discovery = crafter_with_discovery.get_component(RecipeDiscoveryComponent)

    # Create ingredients - moonleaf (herbal) + mana_crystal (magical) = healing_potion
    moonleaf = entity_loader.create_entity("moonleaf", Position(5, 5))
    crystal = entity_loader.create_entity("mana_crystal", Position(5, 5))

    # Craft the item
    result, consumed = crafting_system.craft(
        [moonleaf, crystal], crafter=crafter_with_discovery
    )

    # Recipe should be discovered
    assert discovery.is_discovered("healing_potion") is True


def test_recipe_discovered_event_emitted_on_first_craft(crafter_with_discovery):
    """RecipeDiscoveredEvent is emitted on first successful craft."""
    recipe_loader = RecipeLoader()
    event_bus = EventBus()
    crafting_system = CraftingSystem(recipe_loader=recipe_loader, event_bus=event_bus)
    entity_loader = EntityLoader()

    received_events = []

    def handler(event):
        received_events.append(event)

    event_bus.subscribe("recipe_discovered", handler)

    # Create ingredients
    moonleaf = entity_loader.create_entity("moonleaf", Position(5, 5))
    crystal = entity_loader.create_entity("mana_crystal", Position(5, 5))

    # Craft the item
    crafting_system.craft([moonleaf, crystal], crafter=crafter_with_discovery)

    # Event should be emitted
    assert len(received_events) == 1


def test_recipe_discovered_event_has_correct_data(crafter_with_discovery):
    """RecipeDiscoveredEvent contains correct recipe information."""
    recipe_loader = RecipeLoader()
    event_bus = EventBus()
    crafting_system = CraftingSystem(recipe_loader=recipe_loader, event_bus=event_bus)
    entity_loader = EntityLoader()

    received_events = []

    def handler(event):
        received_events.append(event)

    event_bus.subscribe("recipe_discovered", handler)

    # Create ingredients
    moonleaf = entity_loader.create_entity("moonleaf", Position(5, 5))
    crystal = entity_loader.create_entity("mana_crystal", Position(5, 5))

    # Craft the item
    crafting_system.craft([moonleaf, crystal], crafter=crafter_with_discovery)

    # Event data should be correct
    event = received_events[0]
    assert event.recipe_id == "healing_potion"
    assert event.recipe_name == "Healing Potion"
    assert event.discoverer_name == "Player"


def test_recipe_discovered_event_not_emitted_on_second_craft(crafter_with_discovery):
    """RecipeDiscoveredEvent is not emitted on subsequent crafts."""
    recipe_loader = RecipeLoader()
    event_bus = EventBus()
    crafting_system = CraftingSystem(recipe_loader=recipe_loader, event_bus=event_bus)
    entity_loader = EntityLoader()

    received_events = []

    def handler(event):
        received_events.append(event)

    event_bus.subscribe("recipe_discovered", handler)

    # First craft
    moonleaf1 = entity_loader.create_entity("moonleaf", Position(5, 5))
    crystal1 = entity_loader.create_entity("mana_crystal", Position(5, 5))
    crafting_system.craft([moonleaf1, crystal1], crafter=crafter_with_discovery)

    # Clear events
    received_events.clear()

    # Second craft
    moonleaf2 = entity_loader.create_entity("moonleaf", Position(5, 5))
    crystal2 = entity_loader.create_entity("mana_crystal", Position(5, 5))
    crafting_system.craft([moonleaf2, crystal2], crafter=crafter_with_discovery)

    # Event should not be emitted
    assert len(received_events) == 0


def test_crafting_works_without_recipe_discovery_component(crafter_without_discovery):
    """Crafting still works if crafter has no RecipeDiscoveryComponent."""
    recipe_loader = RecipeLoader()
    event_bus = EventBus()
    crafting_system = CraftingSystem(recipe_loader=recipe_loader, event_bus=event_bus)
    entity_loader = EntityLoader()

    # Create ingredients
    moonleaf = entity_loader.create_entity("moonleaf", Position(5, 5))
    crystal = entity_loader.create_entity("mana_crystal", Position(5, 5))

    # Craft should succeed
    result, consumed = crafting_system.craft(
        [moonleaf, crystal], crafter=crafter_without_discovery
    )

    assert result is not None
    assert result.name == "Healing Potion"


def test_no_discovery_event_without_recipe_discovery_component(crafter_without_discovery):
    """RecipeDiscoveredEvent is not emitted without RecipeDiscoveryComponent."""
    recipe_loader = RecipeLoader()
    event_bus = EventBus()
    crafting_system = CraftingSystem(recipe_loader=recipe_loader, event_bus=event_bus)
    entity_loader = EntityLoader()

    received_events = []

    def handler(event):
        received_events.append(event)

    event_bus.subscribe("recipe_discovered", handler)

    # Create ingredients
    moonleaf = entity_loader.create_entity("moonleaf", Position(5, 5))
    crystal = entity_loader.create_entity("mana_crystal", Position(5, 5))

    # Craft the item
    crafting_system.craft([moonleaf, crystal], crafter=crafter_without_discovery)

    # Event should not be emitted
    assert len(received_events) == 0


def test_multiple_recipes_can_be_discovered(crafter_with_discovery):
    """Multiple different recipes can be discovered."""
    recipe_loader = RecipeLoader()
    event_bus = EventBus()
    crafting_system = CraftingSystem(recipe_loader=recipe_loader, event_bus=event_bus)
    entity_loader = EntityLoader()

    discovery = crafter_with_discovery.get_component(RecipeDiscoveryComponent)

    # First recipe: healing_potion
    moonleaf = entity_loader.create_entity("moonleaf", Position(5, 5))
    crystal = entity_loader.create_entity("mana_crystal", Position(5, 5))
    crafting_system.craft([moonleaf, crystal], crafter=crafter_with_discovery)

    # Second recipe: mana_potion (magical + crystalline)
    crystal2 = entity_loader.create_entity("mana_crystal", Position(5, 5))
    frost = entity_loader.create_entity("frost_essence", Position(5, 5))
    crafting_system.craft([crystal2, frost], crafter=crafter_with_discovery)

    # Both should be discovered
    assert discovery.get_discovery_count() == 2
    assert discovery.is_discovered("healing_potion") is True
    assert discovery.is_discovered("mana_potion") is True


def test_failed_craft_does_not_discover_recipe(crafter_with_discovery):
    """Failed craft does not discover a recipe."""
    recipe_loader = RecipeLoader()
    event_bus = EventBus()
    crafting_system = CraftingSystem(recipe_loader=recipe_loader, event_bus=event_bus)
    entity_loader = EntityLoader()

    discovery = crafter_with_discovery.get_component(RecipeDiscoveryComponent)

    # Create ingredients that don't match any recipe
    moonleaf = entity_loader.create_entity("moonleaf", Position(5, 5))
    iron = entity_loader.create_entity("iron_ore", Position(5, 5))

    # Craft should fail
    result, consumed = crafting_system.craft(
        [moonleaf, iron], crafter=crafter_with_discovery
    )

    # No recipe should be discovered
    assert result is None
    assert discovery.get_discovery_count() == 0
