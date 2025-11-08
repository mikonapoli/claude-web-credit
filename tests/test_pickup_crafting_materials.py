"""Tests for picking up crafting materials."""

import pytest

from roguelike.commands.game_commands import PickupItemCommand
from roguelike.components.entity import ComponentEntity
from roguelike.components.inventory import InventoryComponent
from roguelike.data.entity_loader import EntityLoader
from roguelike.engine.events import EventBus
from roguelike.systems.ai_system import AISystem
from roguelike.systems.combat_system import CombatSystem
from roguelike.systems.movement_system import MovementSystem
from roguelike.systems.status_effects import StatusEffectsSystem
from roguelike.ui.message_log import MessageLog
from roguelike.utils.position import Position
from roguelike.world.game_map import GameMap


@pytest.fixture
def event_bus():
    """Create event bus for testing."""
    return EventBus()


@pytest.fixture
def game_map():
    """Create game map for testing."""
    return GameMap(width=80, height=50)


@pytest.fixture
def combat_system(event_bus):
    """Create combat system for testing."""
    return CombatSystem(event_bus)


@pytest.fixture
def movement_system(game_map):
    """Create movement system for testing."""
    return MovementSystem(game_map)


@pytest.fixture
def status_effects_system(event_bus):
    """Create status effects system for testing."""
    return StatusEffectsSystem(event_bus)


@pytest.fixture
def ai_system(combat_system, movement_system, game_map, status_effects_system):
    """Create AI system for testing."""
    return AISystem(combat_system, movement_system, game_map, status_effects_system)


@pytest.fixture
def message_log():
    """Create message log for testing."""
    return MessageLog()


@pytest.fixture
def player():
    """Create player entity with inventory for testing."""
    player = ComponentEntity(
        position=Position(10, 10),
        char="@",
        name="Player",
        blocks_movement=True,
    )
    player.add_component(InventoryComponent(capacity=20))
    return player


@pytest.fixture
def entity_loader():
    """Create entity loader for testing."""
    return EntityLoader()


def test_pickup_crafting_material(
    player, entity_loader, message_log, ai_system, combat_system, status_effects_system
):
    """Test picking up a crafting material from the ground."""
    # Create a crafting material at player's position
    moonleaf = entity_loader.create_entity("moonleaf", player.position)
    entities = [moonleaf]

    # Create pickup command
    cmd = PickupItemCommand(
        player, entities, message_log, ai_system, combat_system, status_effects_system
    )
    result = cmd.execute()

    # Should succeed
    assert result.success is True
    assert result.turn_consumed is True

    # Material should be removed from world
    assert moonleaf not in entities

    # Material should be in player's inventory
    inventory = player.get_component(InventoryComponent)
    assert moonleaf in inventory.get_items()
    assert len(inventory.get_items()) == 1


def test_pickup_multiple_crafting_materials(
    player, entity_loader, message_log, ai_system, combat_system, status_effects_system
):
    """Test picking up multiple crafting materials."""
    # Create multiple crafting materials at player's position
    moonleaf = entity_loader.create_entity("moonleaf", player.position)
    crystal = entity_loader.create_entity("mana_crystal", player.position)
    entities = [moonleaf, crystal]

    # Pick up first material
    cmd1 = PickupItemCommand(
        player, entities, message_log, ai_system, combat_system, status_effects_system
    )
    result1 = cmd1.execute()
    assert result1.success is True

    # Pick up second material
    cmd2 = PickupItemCommand(
        player, entities, message_log, ai_system, combat_system, status_effects_system
    )
    result2 = cmd2.execute()
    assert result2.success is True

    # Both should be in inventory
    inventory = player.get_component(InventoryComponent)
    assert len(inventory.get_items()) == 2
    assert moonleaf in inventory.get_items()
    assert crystal in inventory.get_items()


def test_pickup_no_items_at_position(
    player, message_log, ai_system, combat_system, status_effects_system
):
    """Test pickup when no items are at player's position."""
    entities = []

    # Create pickup command
    cmd = PickupItemCommand(
        player, entities, message_log, ai_system, combat_system, status_effects_system
    )
    result = cmd.execute()

    # Should fail
    assert result.success is False
    assert result.turn_consumed is False


def test_pickup_material_different_position(
    player, entity_loader, message_log, ai_system, combat_system, status_effects_system
):
    """Test that materials at different positions can't be picked up."""
    # Create material at different position
    moonleaf = entity_loader.create_entity("moonleaf", Position(15, 15))
    entities = [moonleaf]

    # Create pickup command
    cmd = PickupItemCommand(
        player, entities, message_log, ai_system, combat_system, status_effects_system
    )
    result = cmd.execute()

    # Should fail - material is not at player's position
    assert result.success is False
    assert result.turn_consumed is False

    # Material should still be in world
    assert moonleaf in entities


def test_pickup_inventory_full(
    player, entity_loader, message_log, ai_system, combat_system, status_effects_system
):
    """Test pickup when inventory is full."""
    # Fill inventory
    inventory = player.get_component(InventoryComponent)
    for i in range(inventory.capacity):
        material = entity_loader.create_entity("moonleaf", Position(0, 0))
        inventory.add_item(material)

    assert inventory.is_full()

    # Try to pick up another material
    crystal = entity_loader.create_entity("mana_crystal", player.position)
    entities = [crystal]

    cmd = PickupItemCommand(
        player, entities, message_log, ai_system, combat_system, status_effects_system
    )
    result = cmd.execute()

    # Should fail - inventory is full
    assert result.success is False
    assert result.turn_consumed is False

    # Material should still be in world
    assert crystal in entities
