"""Tests for item commands."""

import pytest

from roguelike.commands.actions import PickupItemCommand, UseItemCommand
from roguelike.engine.events import EventBus
from roguelike.entities.item import create_healing_potion, create_strength_potion
from roguelike.entities.player import Player
from roguelike.systems.item_system import ItemSystem
from roguelike.utils.position import Position


@pytest.fixture
def event_bus():
    """Create an event bus for testing."""
    return EventBus()


@pytest.fixture
def player():
    """Create a test player."""
    return Player(position=Position(5, 5))


@pytest.fixture
def item_system(event_bus):
    """Create an item system for testing."""
    return ItemSystem(event_bus)


def test_pickup_item_adds_to_inventory(player, event_bus):
    """Pickup command adds item to inventory."""
    items = [create_healing_potion(Position(5, 5))]
    command = PickupItemCommand(player, items, event_bus)

    command.execute()

    assert len(player.inventory) == 1


def test_pickup_item_removes_from_map(player, event_bus):
    """Pickup command removes item from map."""
    items = [create_healing_potion(Position(5, 5))]
    command = PickupItemCommand(player, items, event_bus)

    command.execute()

    assert len(items) == 0


def test_pickup_item_returns_success(player, event_bus):
    """Pickup command returns success when item picked up."""
    items = [create_healing_potion(Position(5, 5))]
    command = PickupItemCommand(player, items, event_bus)

    result = command.execute()

    assert result.success is True


def test_pickup_item_consumes_turn(player, event_bus):
    """Pickup command consumes a turn."""
    items = [create_healing_potion(Position(5, 5))]
    command = PickupItemCommand(player, items, event_bus)

    result = command.execute()

    assert result.turn_consumed is True


def test_pickup_no_item_returns_failure(player, event_bus):
    """Pickup command returns failure when no item present."""
    items = []
    command = PickupItemCommand(player, items, event_bus)

    result = command.execute()

    assert result.success is False


def test_pickup_no_item_no_turn_consumed(player, event_bus):
    """Pickup command doesn't consume turn when no item present."""
    items = []
    command = PickupItemCommand(player, items, event_bus)

    result = command.execute()

    assert result.turn_consumed is False


def test_pickup_wrong_position_returns_failure(player, event_bus):
    """Pickup command fails when item is not at player position."""
    items = [create_healing_potion(Position(10, 10))]
    command = PickupItemCommand(player, items, event_bus)

    result = command.execute()

    assert result.success is False


def test_pickup_full_inventory_returns_failure(player, event_bus):
    """Pickup command fails when inventory is full."""
    items = [create_healing_potion(Position(5, 5))]
    # Fill inventory
    for _ in range(26):
        player.inventory.add(create_healing_potion(Position(0, 0)))
    command = PickupItemCommand(player, items, event_bus)

    result = command.execute()

    assert result.success is False


def test_pickup_full_inventory_item_stays_on_map(player, event_bus):
    """Item stays on map when inventory is full."""
    items = [create_healing_potion(Position(5, 5))]
    # Fill inventory
    for _ in range(26):
        player.inventory.add(create_healing_potion(Position(0, 0)))
    command = PickupItemCommand(player, items, event_bus)

    command.execute()

    assert len(items) == 1


def test_pickup_emits_event(player, event_bus):
    """Pickup command emits item pickup event."""
    items = [create_healing_potion(Position(5, 5))]
    events = []
    event_bus.subscribe("item_pickup", lambda e: events.append(e))
    command = PickupItemCommand(player, items, event_bus)

    command.execute()

    assert len(events) == 1


def test_pickup_event_has_correct_item_name(player, event_bus):
    """Pickup event contains correct item name."""
    items = [create_healing_potion(Position(5, 5))]
    events = []
    event_bus.subscribe("item_pickup", lambda e: events.append(e))
    command = PickupItemCommand(player, items, event_bus)

    command.execute()

    assert events[0].item_name == "Healing Potion"


def test_use_item_applies_effect(player, item_system):
    """Use item command applies item effect."""
    player.hp = 10
    player.inventory.add(create_healing_potion(Position(5, 5)))
    command = UseItemCommand(player, 0, item_system)

    command.execute()

    assert player.hp == 30


def test_use_item_removes_from_inventory(player, item_system):
    """Use item command removes item from inventory."""
    player.hp = 10
    player.inventory.add(create_healing_potion(Position(5, 5)))
    command = UseItemCommand(player, 0, item_system)

    command.execute()

    assert len(player.inventory) == 0


def test_use_item_returns_success(player, item_system):
    """Use item command returns success."""
    player.hp = 10
    player.inventory.add(create_healing_potion(Position(5, 5)))
    command = UseItemCommand(player, 0, item_system)

    result = command.execute()

    assert result.success is True


def test_use_item_consumes_turn(player, item_system):
    """Use item command consumes a turn."""
    player.hp = 10
    player.inventory.add(create_healing_potion(Position(5, 5)))
    command = UseItemCommand(player, 0, item_system)

    result = command.execute()

    assert result.turn_consumed is True


def test_use_invalid_index_returns_failure(player, item_system):
    """Use item command fails with invalid index."""
    command = UseItemCommand(player, 0, item_system)

    result = command.execute()

    assert result.success is False


def test_use_invalid_index_no_turn_consumed(player, item_system):
    """Use item command doesn't consume turn with invalid index."""
    command = UseItemCommand(player, 0, item_system)

    result = command.execute()

    assert result.turn_consumed is False


def test_use_item_at_full_hp_returns_failure(player, item_system):
    """Use healing item at full HP returns failure."""
    player.inventory.add(create_healing_potion(Position(5, 5)))
    command = UseItemCommand(player, 0, item_system)

    result = command.execute()

    assert result.success is False


def test_use_item_at_full_hp_stays_in_inventory(player, item_system):
    """Healing item stays in inventory if not used."""
    player.inventory.add(create_healing_potion(Position(5, 5)))
    command = UseItemCommand(player, 0, item_system)

    command.execute()

    assert len(player.inventory) == 1


def test_use_strength_potion_increases_power(player, item_system):
    """Using strength potion increases power."""
    initial_power = player.power
    player.inventory.add(create_strength_potion(Position(5, 5)))
    command = UseItemCommand(player, 0, item_system)

    command.execute()

    assert player.power == initial_power + 3
