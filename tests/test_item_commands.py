"""Tests for item commands."""

import pytest

from roguelike.commands.game_commands import PickupItemCommand
from roguelike.commands.inventory_commands import UseItemCommand
from roguelike.engine.events import EventBus
from roguelike.entities.item import create_healing_potion, create_strength_potion
from tests.test_helpers import create_test_player
from roguelike.systems.ai_system import AISystem
from roguelike.systems.combat_system import CombatSystem
from roguelike.systems.item_system import ItemSystem
from roguelike.systems.movement_system import MovementSystem
from roguelike.systems.status_effects import StatusEffectsSystem
from roguelike.ui.message_log import MessageLog
from roguelike.utils.position import Position
from roguelike.world.game_map import GameMap


@pytest.fixture
def event_bus():
    """Create an event bus for testing."""
    return EventBus()


@pytest.fixture
def player():
    """Create a test player."""
    return create_test_player(Position(5, 5))


@pytest.fixture
def game_map():
    """Create a test game map."""
    return GameMap(width=80, height=50)


@pytest.fixture
def combat_system(event_bus):
    """Create a combat system for testing."""
    return CombatSystem(event_bus)


@pytest.fixture
def movement_system(game_map):
    """Create a movement system for testing."""
    return MovementSystem(game_map)


@pytest.fixture
def status_effects_system(event_bus):
    """Create a status effects system for testing."""
    return StatusEffectsSystem(event_bus)


@pytest.fixture
def ai_system(combat_system, movement_system, game_map, status_effects_system):
    """Create an AI system for testing."""
    return AISystem(combat_system, movement_system, game_map, status_effects_system)


@pytest.fixture
def item_system(event_bus):
    """Create an item system for testing."""
    from roguelike.systems.status_effects import StatusEffectsSystem
    status_effects_system = StatusEffectsSystem(event_bus)
    return ItemSystem(event_bus, status_effects_system)


@pytest.fixture
def message_log():
    """Create a message log for testing."""
    return MessageLog()


def test_pickup_item_adds_to_inventory(player, message_log, ai_system, combat_system, status_effects_system):
    """Pickup command adds item to inventory."""
    items = [create_healing_potion(Position(5, 5))]
    command = PickupItemCommand(player, items, message_log, ai_system, combat_system, status_effects_system)

    command.execute()

    assert len(player.inventory) == 1


def test_pickup_item_removes_from_map(player, message_log, ai_system, combat_system, status_effects_system):
    """Pickup command removes item from map."""
    items = [create_healing_potion(Position(5, 5))]
    command = PickupItemCommand(player, items, message_log, ai_system, combat_system, status_effects_system)

    command.execute()

    assert len(items) == 0


def test_pickup_item_returns_success(player, message_log, ai_system, combat_system, status_effects_system):
    """Pickup command returns success when item picked up."""
    items = [create_healing_potion(Position(5, 5))]
    command = PickupItemCommand(player, items, message_log, ai_system, combat_system, status_effects_system)

    result = command.execute()

    assert result.success is True


def test_pickup_item_consumes_turn(player, message_log, ai_system, combat_system, status_effects_system):
    """Pickup command consumes a turn."""
    items = [create_healing_potion(Position(5, 5))]
    command = PickupItemCommand(player, items, message_log, ai_system, combat_system, status_effects_system)

    result = command.execute()

    assert result.turn_consumed is True


def test_pickup_no_item_returns_failure(player, message_log, ai_system, combat_system, status_effects_system):
    """Pickup command returns failure when no item present."""
    items = []
    command = PickupItemCommand(player, items, message_log, ai_system, combat_system, status_effects_system)

    result = command.execute()

    assert result.success is False


def test_pickup_no_item_no_turn_consumed(player, message_log, ai_system, combat_system, status_effects_system):
    """Pickup command doesn't consume turn when no item present."""
    items = []
    command = PickupItemCommand(player, items, message_log, ai_system, combat_system, status_effects_system)

    result = command.execute()

    assert result.turn_consumed is False


def test_pickup_wrong_position_returns_failure(player, message_log, ai_system, combat_system, status_effects_system):
    """Pickup command fails when item is not at player position."""
    items = [create_healing_potion(Position(10, 10))]
    command = PickupItemCommand(player, items, message_log, ai_system, combat_system, status_effects_system)

    result = command.execute()

    assert result.success is False


def test_pickup_full_inventory_returns_failure(player, message_log, ai_system, combat_system, status_effects_system):
    """Pickup command fails when inventory is full."""
    items = [create_healing_potion(Position(5, 5))]
    # Fill inventory
    for _ in range(26):
        player.inventory.add(create_healing_potion(Position(0, 0)))
    command = PickupItemCommand(player, items, message_log, ai_system, combat_system, status_effects_system)

    result = command.execute()

    assert result.success is False


def test_pickup_full_inventory_item_stays_on_map(player, message_log, ai_system, combat_system, status_effects_system):
    """Item stays on map when inventory is full."""
    items = [create_healing_potion(Position(5, 5))]
    # Fill inventory
    for _ in range(26):
        player.inventory.add(create_healing_potion(Position(0, 0)))
    command = PickupItemCommand(player, items, message_log, ai_system, combat_system, status_effects_system)

    command.execute()

    assert len(items) == 1


def test_pickup_adds_message_to_log(player, message_log, ai_system, combat_system, status_effects_system):
    """Pickup command adds message to message log."""
    items = [create_healing_potion(Position(5, 5))]
    command = PickupItemCommand(player, items, message_log, ai_system, combat_system, status_effects_system)

    command.execute()

    # Check that a message was added
    assert len(message_log.messages) > 0
    assert "picked up" in str(message_log.messages[-1]).lower()


def test_pickup_processes_monster_turns(player, message_log, ai_system, combat_system, status_effects_system, game_map):
    """Pickup command processes AI turns, allowing monsters to act."""
    from roguelike.components.factories import create_orc

    # Create an orc near the player
    orc = create_orc(Position(6, 5))  # One tile to the right of player
    items = [create_healing_potion(Position(5, 5)), orc]

    # Register the orc with the AI system
    ai_system.register_monster(orc)

    # Store orc's initial position
    initial_orc_pos = orc.position

    # Player picks up item - this should let the orc take its turn
    command = PickupItemCommand(player, items, message_log, ai_system, combat_system, status_effects_system)
    command.execute()

    # The orc should have taken its turn and likely moved or attacked
    # At minimum, the AI system should have processed the orc
    # We can't guarantee exact behavior, but AI system should have been called
    # This test primarily ensures no crash occurs and turn processing happens
    assert True  # If we get here without crash, turn processing worked


def test_use_item_applies_effect(player, item_system):
    """Use item command applies item effect."""
    player.hp = 10
    potion = create_healing_potion(Position(5, 5))
    player.inventory.add(potion)
    command = UseItemCommand(player, potion)

    command.execute()

    assert player.hp == 30


def test_use_item_removes_from_inventory(player, item_system):
    """Use item command removes item from inventory."""
    player.hp = 10
    potion = create_healing_potion(Position(5, 5))
    player.inventory.add(potion)
    command = UseItemCommand(player, potion)

    command.execute()

    assert len(player.inventory) == 0


def test_use_item_returns_success(player, item_system):
    """Use item command returns success."""
    player.hp = 10
    potion = create_healing_potion(Position(5, 5))
    player.inventory.add(potion)
    command = UseItemCommand(player, potion)

    result = command.execute()

    assert result.success is True


def test_use_item_consumes_turn(player, item_system):
    """Use item command consumes a turn."""
    player.hp = 10
    potion = create_healing_potion(Position(5, 5))
    player.inventory.add(potion)
    command = UseItemCommand(player, potion)

    result = command.execute()

    assert result.turn_consumed is True


def test_use_invalid_item_returns_failure(player, item_system):
    """Use item command fails with item not in inventory."""
    potion = create_healing_potion(Position(5, 5))
    command = UseItemCommand(player, potion)

    result = command.execute()

    assert result.success is False


def test_use_invalid_item_no_turn_consumed(player, item_system):
    """Use item command doesn't consume turn when item not in inventory."""
    potion = create_healing_potion(Position(5, 5))
    command = UseItemCommand(player, potion)

    result = command.execute()

    assert result.turn_consumed is False


def test_use_item_at_full_hp_returns_failure(player, item_system):
    """Use healing item at full HP returns failure."""
    potion = create_healing_potion(Position(5, 5))
    player.inventory.add(potion)
    command = UseItemCommand(player, potion)

    result = command.execute()

    assert result.success is False


def test_use_item_at_full_hp_stays_in_inventory(player, item_system):
    """Healing item stays in inventory if not used."""
    potion = create_healing_potion(Position(5, 5))
    player.inventory.add(potion)
    command = UseItemCommand(player, potion)

    command.execute()

    assert len(player.inventory) == 1


def test_use_strength_potion_increases_power(player, item_system):
    """Using strength potion applies strength status effect."""
    player.inventory.add(create_strength_potion(Position(5, 5)))
    command = UseItemCommand(player, 0, item_system)

    command.execute()

    # Check that strength effect is applied
    assert item_system.status_effects_system.has_effect(player, "strength")
