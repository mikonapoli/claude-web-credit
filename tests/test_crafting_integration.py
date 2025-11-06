"""Integration tests for crafting system with game engine."""

import pytest

from roguelike.commands.inventory_commands import CraftCommand
from roguelike.components.crafting import CraftingComponent
from roguelike.components.entity import ComponentEntity
from roguelike.components.inventory import InventoryComponent
from roguelike.data.entity_loader import EntityLoader
from roguelike.data.recipe_loader import RecipeLoader
from roguelike.engine.events import EventBus
from roguelike.systems.crafting import CraftingSystem
from roguelike.utils.position import Position


@pytest.fixture
def entity_loader():
    """Create entity loader."""
    return EntityLoader()


@pytest.fixture
def recipe_loader():
    """Create recipe loader."""
    return RecipeLoader()


@pytest.fixture
def event_bus():
    """Create event bus."""
    return EventBus()


@pytest.fixture
def crafting_system(recipe_loader, event_bus):
    """Create crafting system."""
    return CraftingSystem(recipe_loader, event_bus)


@pytest.fixture
def player():
    """Create a test player with inventory."""
    player = ComponentEntity(
        position=Position(5, 5),
        char="@",
        name="Player",
        blocks_movement=True,
    )
    player.add_component(InventoryComponent(capacity=10))
    return player


def test_craft_command_crafts_healing_potion(player, crafting_system, entity_loader):
    """CraftCommand successfully crafts a healing potion."""
    # Add crafting materials to player inventory
    moonleaf = entity_loader.create_entity("moonleaf", Position(0, 0))
    crystal = entity_loader.create_entity("mana_crystal", Position(0, 0))

    inventory = player.get_component(InventoryComponent)
    inventory.add_item(moonleaf)
    inventory.add_item(crystal)

    # Execute craft command
    command = CraftCommand(player, [moonleaf, crystal], crafting_system)
    result = command.execute()

    # Should succeed and consume a turn
    assert result.success
    assert result.turn_consumed

    # Ingredients should be removed from inventory
    assert moonleaf not in inventory.get_items()
    assert crystal not in inventory.get_items()

    # Result should be in inventory
    items = inventory.get_items()
    assert len(items) == 1
    assert items[0].name == "Healing Potion"


def test_craft_command_fails_with_no_recipe(player, crafting_system, entity_loader):
    """CraftCommand fails when no matching recipe exists."""
    # Add items that don't match any recipe
    moonleaf1 = entity_loader.create_entity("moonleaf", Position(0, 0))
    moonleaf2 = entity_loader.create_entity("moonleaf", Position(0, 0))

    inventory = player.get_component(InventoryComponent)
    inventory.add_item(moonleaf1)
    inventory.add_item(moonleaf2)

    # Execute craft command
    command = CraftCommand(player, [moonleaf1, moonleaf2], crafting_system)
    result = command.execute()

    # Should fail
    assert not result.success
    assert not result.turn_consumed

    # Ingredients should remain in inventory
    assert moonleaf1 in inventory.get_items()
    assert moonleaf2 in inventory.get_items()


def test_craft_command_crafts_antidote(player, crafting_system, entity_loader):
    """CraftCommand successfully crafts an antidote."""
    # Add crafting materials for antidote (herbal + purifying)
    moonleaf = entity_loader.create_entity("moonleaf", Position(0, 0))
    salt = entity_loader.create_entity("purifying_salt", Position(0, 0))

    inventory = player.get_component(InventoryComponent)
    inventory.add_item(moonleaf)
    inventory.add_item(salt)

    # Execute craft command
    command = CraftCommand(player, [moonleaf, salt], crafting_system)
    result = command.execute()

    # Should succeed
    assert result.success
    assert result.turn_consumed

    # Result should be antidote
    items = inventory.get_items()
    assert len(items) == 1
    assert items[0].name == "Antidote"


def test_craft_command_with_three_ingredients(player, crafting_system, entity_loader):
    """CraftCommand successfully crafts with three ingredients."""
    # Add materials for strength elixir (herbal + magical + rare)
    moonleaf = entity_loader.create_entity("moonleaf", Position(0, 0))
    crystal = entity_loader.create_entity("mana_crystal", Position(0, 0))
    dragon_scale = entity_loader.create_entity("dragon_scale", Position(0, 0))

    inventory = player.get_component(InventoryComponent)
    inventory.add_item(moonleaf)
    inventory.add_item(crystal)
    inventory.add_item(dragon_scale)

    # Execute craft command
    command = CraftCommand(player, [moonleaf, crystal, dragon_scale], crafting_system)
    result = command.execute()

    # Should succeed
    assert result.success
    assert result.turn_consumed

    # Result should be strength elixir
    items = inventory.get_items()
    assert len(items) == 1
    assert items[0].name == "Strength Elixir"


def test_craft_command_fails_when_ingredient_not_in_inventory(player, crafting_system, entity_loader):
    """CraftCommand fails when ingredient is not in player inventory."""
    # Create items but don't add to inventory
    moonleaf = entity_loader.create_entity("moonleaf", Position(0, 0))
    crystal = entity_loader.create_entity("mana_crystal", Position(0, 0))

    # Execute craft command without adding to inventory
    command = CraftCommand(player, [moonleaf, crystal], crafting_system)
    result = command.execute()

    # Should fail
    assert not result.success
    assert not result.turn_consumed


def test_crafting_materials_spawn_in_dungeon(entity_loader):
    """Crafting materials can be spawned via entity loader."""
    # Test a few key crafting materials
    materials = [
        "moonleaf",
        "mana_crystal",
        "nightshade",
        "purifying_salt",
        "dragon_scale",
        "ancient_parchment",
    ]

    for material_type in materials:
        item = entity_loader.create_entity(material_type, Position(5, 5))
        assert item is not None
        assert item.name is not None

        # Should have crafting component
        crafting_comp = item.get_component(CraftingComponent)
        assert crafting_comp is not None
        assert len(crafting_comp.tags) > 0


def test_crafting_emits_event(player, crafting_system, entity_loader, event_bus):
    """Crafting emits a CraftingAttemptEvent."""
    events_received = []

    def event_handler(event):
        events_received.append(event)

    event_bus.subscribe("crafting_attempt", event_handler)

    # Add crafting materials
    moonleaf = entity_loader.create_entity("moonleaf", Position(0, 0))
    crystal = entity_loader.create_entity("mana_crystal", Position(0, 0))

    inventory = player.get_component(InventoryComponent)
    inventory.add_item(moonleaf)
    inventory.add_item(crystal)

    # Execute craft command
    command = CraftCommand(player, [moonleaf, crystal], crafting_system)
    command.execute()

    # Should have received event
    assert len(events_received) == 1
    event = events_received[0]
    assert event.success
    assert event.result_name == "Healing Potion"
    assert event.crafter_name == "Player"
