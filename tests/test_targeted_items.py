"""Tests for targeted item usage."""

import pytest

from roguelike.engine.events import EventBus
from roguelike.entities.item import create_scroll_confusion, create_healing_potion, ItemType
from roguelike.components.factories import create_orc, create_troll
from tests.test_helpers import create_test_player
from roguelike.systems.item_system import ItemSystem
from roguelike.systems.status_effects import StatusEffectsSystem
from roguelike.utils.position import Position


def test_confusion_scroll_requires_targeting():
    """Confusion scroll requires targeting."""
    scroll = create_scroll_confusion(Position(0, 0))
    assert scroll.requires_targeting() is True


def test_healing_potion_does_not_require_targeting():
    """Healing potion does not require targeting."""
    potion = create_healing_potion(Position(0, 0))
    assert potion.requires_targeting() is False


def test_confusion_scroll_applies_to_target():
    """Confusion scroll applies confusion to target monster."""
    event_bus = EventBus()
    status_system = StatusEffectsSystem(event_bus)
    item_system = ItemSystem(event_bus, status_system)

    player = Player(Position(5, 5))
    orc = create_orc(Position(7, 7))
    scroll = create_scroll_confusion(Position(0, 0))

    # Use scroll on orc
    success = item_system.use_item(scroll, player, player.inventory, target=orc)

    assert success is True
    assert status_system.has_effect(orc, "confusion") is True


def test_confusion_scroll_fails_without_target():
    """Confusion scroll fails when no target provided."""
    event_bus = EventBus()
    status_system = StatusEffectsSystem(event_bus)
    item_system = ItemSystem(event_bus, status_system)

    player = Player(Position(5, 5))
    scroll = create_scroll_confusion(Position(0, 0))

    # Use scroll without target
    success = item_system.use_item(scroll, player, player.inventory, target=None)

    assert success is False


def test_confusion_scroll_fails_on_dead_target():
    """Confusion scroll fails when target is dead."""
    event_bus = EventBus()
    status_system = StatusEffectsSystem(event_bus)
    item_system = ItemSystem(event_bus, status_system)

    player = Player(Position(5, 5))
    orc = create_orc(Position(7, 7))
    orc.take_damage(100)  # Kill orc
    scroll = create_scroll_confusion(Position(0, 0))

    # Use scroll on dead orc
    success = item_system.use_item(scroll, player, player.inventory, target=orc)

    assert success is False


def test_confusion_scroll_with_correct_duration():
    """Confusion scroll applies effect with correct duration."""
    event_bus = EventBus()
    status_system = StatusEffectsSystem(event_bus)
    item_system = ItemSystem(event_bus, status_system)

    player = Player(Position(5, 5))
    orc = create_orc(Position(7, 7))
    scroll = create_scroll_confusion(Position(0, 0))

    # Use scroll on orc
    item_system.use_item(scroll, player, player.inventory, target=orc)

    # Check effect duration matches scroll value (10 turns)
    effect = orc._status_effects.get_effect("confusion")
    assert effect is not None
    assert effect.duration == 10


def test_confusion_scroll_on_multiple_targets():
    """Confusion scroll can be used on multiple targets separately."""
    event_bus = EventBus()
    status_system = StatusEffectsSystem(event_bus)
    item_system = ItemSystem(event_bus, status_system)

    player = Player(Position(5, 5))
    orc = create_orc(Position(7, 7))
    troll = create_troll(Position(10, 10))

    scroll1 = create_scroll_confusion(Position(0, 0))
    scroll2 = create_scroll_confusion(Position(0, 0))

    # Use first scroll on orc
    player.inventory.add(scroll1)
    success1 = item_system.use_item(scroll1, player, player.inventory, target=orc)

    # Use second scroll on troll
    player.inventory.add(scroll2)
    success2 = item_system.use_item(scroll2, player, player.inventory, target=troll)

    assert success1 is True
    assert success2 is True
    assert status_system.has_effect(orc, "confusion") is True
    assert status_system.has_effect(troll, "confusion") is True
