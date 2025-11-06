"""Tests for crafting system integration with game engine."""

import pytest

from roguelike.commands.crafting_commands import CraftItemsCommand
from roguelike.components.entity import ComponentEntity
from roguelike.components.crafting import CraftingComponent
from roguelike.components.inventory import InventoryComponent
from roguelike.components.recipe_discovery import RecipeDiscoveryComponent
from roguelike.data.recipe_loader import RecipeLoader
from roguelike.engine.events import (
    EventBus,
    CraftingAttemptEvent,
    RecipeDiscoveredEvent,
)
from roguelike.systems.crafting import CraftingSystem
from roguelike.utils.position import Position


def test_craft_command_with_valid_recipe():
    """CraftCommand successfully crafts items with valid recipe."""
    # Create crafter with inventory and recipe discovery
    crafter = ComponentEntity(position=Position(0, 0), char="@", name="Player")
    inventory = InventoryComponent(capacity=10)
    discovery = RecipeDiscoveryComponent()
    crafter.add_component(inventory)
    crafter.add_component(discovery)

    # Create ingredients for healing potion (herbal + magical)
    herb = ComponentEntity(position=Position(0, 0), char="%", name="Herb")
    herb.add_component(CraftingComponent(tags={"herbal"}, consumable=True))
    crystal = ComponentEntity(position=Position(0, 0), char="*", name="Crystal")
    crystal.add_component(CraftingComponent(tags={"magical"}, consumable=True))

    # Add to inventory
    inventory.add_item(herb)
    inventory.add_item(crystal)

    # Create crafting system
    recipe_loader = RecipeLoader()
    event_bus = EventBus()
    crafting_system = CraftingSystem(recipe_loader, event_bus)

    # Track events
    events = []
    event_bus.subscribe("crafting_attempt", lambda e: events.append(e))
    event_bus.subscribe("recipe_discovered", lambda e: events.append(e))

    # Create entities list
    entities = []

    # Execute craft command
    command = CraftItemsCommand(
        crafter=crafter,
        ingredients=[herb, crystal],
        crafting_system=crafting_system,
        entities=entities,
    )
    result = command.execute()

    # Verify success
    assert result.success is True
    assert result.turn_consumed is True


def test_craft_command_with_invalid_recipe():
    """CraftCommand fails with invalid recipe combination."""
    # Create crafter with inventory
    crafter = ComponentEntity(position=Position(0, 0), char="@", name="Player")
    inventory = InventoryComponent(capacity=10)
    crafter.add_component(inventory)

    # Create incompatible ingredients
    herb1 = ComponentEntity(position=Position(0, 0), char="%", name="Herb1")
    herb1.add_component(CraftingComponent(tags={"herbal"}, consumable=True))
    herb2 = ComponentEntity(position=Position(0, 0), char="%", name="Herb2")
    herb2.add_component(CraftingComponent(tags={"herbal"}, consumable=True))

    # Add to inventory
    inventory.add_item(herb1)
    inventory.add_item(herb2)

    # Create crafting system
    recipe_loader = RecipeLoader()
    event_bus = EventBus()
    crafting_system = CraftingSystem(recipe_loader, event_bus)

    # Track events
    events = []
    event_bus.subscribe("crafting_attempt", lambda e: events.append(e))

    # Create entities list
    entities = []

    # Execute craft command
    command = CraftItemsCommand(
        crafter=crafter,
        ingredients=[herb1, herb2],
        crafting_system=crafting_system,
        entities=entities,
    )
    result = command.execute()

    # Verify failure
    assert result.success is False
    assert result.turn_consumed is True  # Still consumes a turn


def test_recipe_discovery_on_first_craft():
    """Recipe is discovered when crafted for the first time."""
    # Create crafter with recipe discovery
    crafter = ComponentEntity(position=Position(0, 0), char="@", name="Player")
    inventory = InventoryComponent(capacity=10)
    discovery = RecipeDiscoveryComponent()
    crafter.add_component(inventory)
    crafter.add_component(discovery)

    # Create ingredients
    herb = ComponentEntity(position=Position(0, 0), char="%", name="Herb")
    herb.add_component(CraftingComponent(tags={"herbal"}, consumable=True))
    crystal = ComponentEntity(position=Position(0, 0), char="*", name="Crystal")
    crystal.add_component(CraftingComponent(tags={"magical"}, consumable=True))

    inventory.add_item(herb)
    inventory.add_item(crystal)

    # Create crafting system
    recipe_loader = RecipeLoader()
    event_bus = EventBus()
    crafting_system = CraftingSystem(recipe_loader, event_bus)

    # Track events
    discovery_events = []
    event_bus.subscribe("recipe_discovered", lambda e: discovery_events.append(e))

    # Verify recipe not discovered yet
    assert discovery.get_discovery_count() == 0

    # Craft
    result, _ = crafting_system.craft([herb, crystal], crafter)

    # Verify recipe discovered
    assert result is not None
    assert discovery.get_discovery_count() == 1
    assert discovery.is_discovered("healing_potion") is True
    assert len(discovery_events) == 1
    assert discovery_events[0].recipe_id == "healing_potion"


def test_recipe_not_rediscovered_on_second_craft():
    """Recipe is not discovered again when crafted second time."""
    # Create crafter with recipe discovery
    crafter = ComponentEntity(position=Position(0, 0), char="@", name="Player")
    inventory = InventoryComponent(capacity=10)
    discovery = RecipeDiscoveryComponent()
    crafter.add_component(inventory)
    crafter.add_component(discovery)

    # Mark recipe as already discovered
    discovery.discover_recipe("healing_potion")

    # Create ingredients
    herb = ComponentEntity(position=Position(0, 0), char="%", name="Herb")
    herb.add_component(CraftingComponent(tags={"herbal"}, consumable=True))
    crystal = ComponentEntity(position=Position(0, 0), char="*", name="Crystal")
    crystal.add_component(CraftingComponent(tags={"magical"}, consumable=True))

    inventory.add_item(herb)
    inventory.add_item(crystal)

    # Create crafting system
    recipe_loader = RecipeLoader()
    event_bus = EventBus()
    crafting_system = CraftingSystem(recipe_loader, event_bus)

    # Track events
    discovery_events = []
    event_bus.subscribe("recipe_discovered", lambda e: discovery_events.append(e))

    # Craft again
    result, _ = crafting_system.craft([herb, crystal], crafter)

    # Verify no new discovery
    assert result is not None
    assert discovery.get_discovery_count() == 1  # Still 1
    assert len(discovery_events) == 0  # No events


def test_crafting_events_emitted():
    """Crafting system emits appropriate events."""
    # Create crafter
    crafter = ComponentEntity(position=Position(0, 0), char="@", name="Player")
    inventory = InventoryComponent(capacity=10)
    crafter.add_component(inventory)

    # Create ingredients
    herb = ComponentEntity(position=Position(0, 0), char="%", name="Herb")
    herb.add_component(CraftingComponent(tags={"herbal"}, consumable=True))
    crystal = ComponentEntity(position=Position(0, 0), char="*", name="Crystal")
    crystal.add_component(CraftingComponent(tags={"magical"}, consumable=True))

    # Create crafting system
    recipe_loader = RecipeLoader()
    event_bus = EventBus()
    crafting_system = CraftingSystem(recipe_loader, event_bus)

    # Track events
    craft_events = []
    event_bus.subscribe("crafting_attempt", lambda e: craft_events.append(e))

    # Craft
    result, _ = crafting_system.craft([herb, crystal], crafter)

    # Verify event emitted
    assert len(craft_events) == 1
    event = craft_events[0]
    assert isinstance(event, CraftingAttemptEvent)
    assert event.success is True
    assert event.crafter_name == "Player"
    assert "Herb" in event.ingredient_names
    assert "Crystal" in event.ingredient_names
    assert event.result_name == "Healing Potion"
