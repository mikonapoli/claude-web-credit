"""Tests for item commands."""

import pytest

from roguelike.commands.game_commands import PickupItemCommand
from roguelike.commands.inventory_commands import UseItemCommand
from roguelike.engine.events import EventBus
from roguelike.entities.item import create_healing_potion, create_strength_potion
from tests.test_helpers import create_test_player
from roguelike.systems.item_system import ItemSystem
from roguelike.ui.message_log import MessageLog
from roguelike.utils.position import Position


@pytest.fixture
def event_bus():
    """Create an event bus for testing."""
    return EventBus()


@pytest.fixture
def player():
    """Create a test player."""
    return create_test_player(Position(5, 5))


@pytest.fixture
def item_system(event_bus):
    """Create an item system for testing."""
    return ItemSystem(event_bus)


@pytest.fixture
def message_log():
    """Create a message log for testing."""
    return MessageLog()


def test_pickup_item_adds_to_inventory(player, message_log):
    """Pickup command adds item to inventory."""
    items = [create_healing_potion(Position(5, 5))]
    command = PickupItemCommand(player, items, message_log)

    command.execute()

    assert len(player.inventory) == 1


def test_pickup_item_removes_from_map(player, message_log):
    """Pickup command removes item from map."""
    items = [create_healing_potion(Position(5, 5))]
    command = PickupItemCommand(player, items, message_log)

    command.execute()

    assert len(items) == 0


def test_pickup_item_returns_success(player, message_log):
    """Pickup command returns success when item picked up."""
    items = [create_healing_potion(Position(5, 5))]
    command = PickupItemCommand(player, items, message_log)

    result = command.execute()

    assert result.success is True


def test_pickup_item_consumes_turn(player, message_log):
    """Pickup command consumes a turn."""
    items = [create_healing_potion(Position(5, 5))]
    command = PickupItemCommand(player, items, message_log)

    result = command.execute()

    assert result.turn_consumed is True


def test_pickup_no_item_returns_failure(player, message_log):
    """Pickup command returns failure when no item present."""
    items = []
    command = PickupItemCommand(player, items, message_log)

    result = command.execute()

    assert result.success is False


def test_pickup_no_item_no_turn_consumed(player, message_log):
    """Pickup command doesn't consume turn when no item present."""
    items = []
    command = PickupItemCommand(player, items, message_log)

    result = command.execute()

    assert result.turn_consumed is False


def test_pickup_wrong_position_returns_failure(player, message_log):
    """Pickup command fails when item is not at player position."""
    items = [create_healing_potion(Position(10, 10))]
    command = PickupItemCommand(player, items, message_log)

    result = command.execute()

    assert result.success is False


def test_pickup_full_inventory_returns_failure(player, message_log):
    """Pickup command fails when inventory is full."""
    items = [create_healing_potion(Position(5, 5))]
    # Fill inventory
    for _ in range(26):
        player.inventory.add(create_healing_potion(Position(0, 0)))
    command = PickupItemCommand(player, items, message_log)

    result = command.execute()

    assert result.success is False


def test_pickup_full_inventory_item_stays_on_map(player, message_log):
    """Item stays on map when inventory is full."""
    items = [create_healing_potion(Position(5, 5))]
    # Fill inventory
    for _ in range(26):
        player.inventory.add(create_healing_potion(Position(0, 0)))
    command = PickupItemCommand(player, items, message_log)

    command.execute()

    assert len(items) == 1


def test_pickup_adds_message_to_log(player, message_log):
    """Pickup command adds message to message log."""
    items = [create_healing_potion(Position(5, 5))]
    command = PickupItemCommand(player, items, message_log)

    command.execute()

    # Check that a message was added
    assert len(message_log.messages) > 0
    assert "picked up" in str(message_log.messages[-1]).lower()

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
    """Using strength potion increases power."""
    initial_power = player.power
    potion = create_strength_potion(Position(5, 5))
    player.inventory.add(potion)
    command = UseItemCommand(player, potion)

    command.execute()

    assert player.power == initial_power + 3
