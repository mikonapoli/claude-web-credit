"""Tests for item system."""

import pytest

from roguelike.engine.events import EventBus, HealingEvent, ItemUseEvent
from roguelike.entities.actor import Actor
from roguelike.entities.item import (
    create_cheese_wheel,
    create_cursed_ring,
    create_greater_healing_potion,
    create_healing_potion,
    create_strength_potion,
)
from roguelike.systems.inventory import Inventory
from roguelike.systems.item_system import ItemSystem
from roguelike.utils.position import Position


@pytest.fixture
def event_bus():
    """Create an event bus for testing."""
    return EventBus()


@pytest.fixture
def item_system(event_bus):
    """Create an item system for testing."""
    from roguelike.systems.status_effects import StatusEffectsSystem
    status_effects_system = StatusEffectsSystem(event_bus)
    return ItemSystem(event_bus, status_effects_system)


@pytest.fixture
def player():
    """Create a test player."""
    return Actor(
        position=Position(5, 5),
        char="@",
        name="Player",
        max_hp=30,
        defense=2,
        power=5,
    )


@pytest.fixture
def inventory():
    """Create an inventory for testing."""
    return Inventory(capacity=10)


def test_healing_potion_heals_player(item_system, player, inventory):
    """Healing potion restores HP."""
    player.hp = 10
    potion = create_healing_potion(Position(5, 5))
    inventory.add(potion)

    item_system.use_item(potion, player, inventory)

    assert player.hp == 30


def test_healing_potion_removed_from_inventory(item_system, player, inventory):
    """Healing potion is removed after use."""
    player.hp = 10
    potion = create_healing_potion(Position(5, 5))
    inventory.add(potion)

    item_system.use_item(potion, player, inventory)

    assert len(inventory) == 0


def test_healing_potion_at_full_hp_not_used(item_system, player, inventory):
    """Healing potion cannot be used at full HP."""
    potion = create_healing_potion(Position(5, 5))
    inventory.add(potion)

    result = item_system.use_item(potion, player, inventory)

    assert result is False


def test_healing_potion_at_full_hp_not_removed(item_system, player, inventory):
    """Healing potion stays in inventory if not used."""
    potion = create_healing_potion(Position(5, 5))
    inventory.add(potion)

    item_system.use_item(potion, player, inventory)

    assert len(inventory) == 1


def test_healing_potion_emits_item_use_event(item_system, player, inventory, event_bus):
    """Using healing potion emits item use event."""
    player.hp = 10
    potion = create_healing_potion(Position(5, 5))
    inventory.add(potion)
    events = []
    event_bus.subscribe("item_use", lambda e: events.append(e))

    item_system.use_item(potion, player, inventory)

    assert len(events) == 1


def test_healing_potion_emits_healing_event(item_system, player, inventory, event_bus):
    """Using healing potion emits healing event."""
    player.hp = 10
    potion = create_healing_potion(Position(5, 5))
    inventory.add(potion)
    events = []
    event_bus.subscribe("healing", lambda e: events.append(e))

    item_system.use_item(potion, player, inventory)

    assert len(events) == 1


def test_healing_event_has_correct_amount(item_system, player, inventory, event_bus):
    """Healing event contains correct healing amount."""
    player.hp = 10
    potion = create_healing_potion(Position(5, 5))
    inventory.add(potion)
    events = []
    event_bus.subscribe("healing", lambda e: events.append(e))

    item_system.use_item(potion, player, inventory)

    assert events[0].amount_healed == 20


def test_greater_healing_potion_heals_more(item_system, player, inventory):
    """Greater healing potion restores more HP."""
    player.hp = 10
    potion = create_greater_healing_potion(Position(5, 5))
    inventory.add(potion)

    item_system.use_item(potion, player, inventory)

    assert player.hp == 30


def test_cheese_wheel_heals_large_amount(item_system, player, inventory):
    """Cheese wheel restores large amount of HP."""
    player.hp = 1
    cheese = create_cheese_wheel(Position(5, 5))
    inventory.add(cheese)

    item_system.use_item(cheese, player, inventory)

    assert player.hp == 30


def test_healing_capped_at_max_hp(item_system, player, inventory):
    """Healing cannot exceed max HP."""
    player.hp = 25
    potion = create_healing_potion(Position(5, 5))
    inventory.add(potion)

    item_system.use_item(potion, player, inventory)

    assert player.hp == 30


def test_strength_potion_increases_power(item_system, player, inventory):
    """Strength potion applies strength status effect."""
    potion = create_strength_potion(Position(5, 5))
    inventory.add(potion)

    item_system.use_item(potion, player, inventory)

    # Check that strength effect is applied
    assert item_system.status_effects_system.has_effect(player, "strength")


def test_strength_potion_removed_after_use(item_system, player, inventory):
    """Strength potion is removed after use."""
    potion = create_strength_potion(Position(5, 5))
    inventory.add(potion)

    result = item_system.use_item(potion, player, inventory)

    # Should succeed and be removed from inventory
    assert result is True
    assert len(inventory) == 0


def test_use_item_returns_true_on_success(item_system, player, inventory):
    """use_item returns True when item is used successfully."""
    player.hp = 10
    potion = create_healing_potion(Position(5, 5))
    inventory.add(potion)

    result = item_system.use_item(potion, player, inventory)

    assert result is True


def test_item_use_event_has_correct_item_name(item_system, player, inventory, event_bus):
    """Item use event contains correct item name."""
    player.hp = 10
    potion = create_healing_potion(Position(5, 5))
    inventory.add(potion)
    events = []
    event_bus.subscribe("item_use", lambda e: events.append(e))

    item_system.use_item(potion, player, inventory)

    assert events[0].item_name == "Healing Potion"


def test_item_use_event_has_correct_user_name(item_system, player, inventory, event_bus):
    """Item use event contains correct user name."""
    player.hp = 10
    potion = create_healing_potion(Position(5, 5))
    inventory.add(potion)
    events = []
    event_bus.subscribe("item_use", lambda e: events.append(e))

    item_system.use_item(potion, player, inventory)

    assert events[0].entity_name == "Player"


def test_healing_event_has_correct_entity_name(item_system, player, inventory, event_bus):
    """Healing event contains correct entity name."""
    player.hp = 10
    potion = create_healing_potion(Position(5, 5))
    inventory.add(potion)
    events = []
    event_bus.subscribe("healing", lambda e: events.append(e))

    item_system.use_item(potion, player, inventory)

    assert events[0].entity_name == "Player"
