"""Tests for item spawning in procgen."""

import random

import pytest

from roguelike.entities.item import ItemType
from roguelike.utils.position import Position
from roguelike.world.procgen import place_items
from roguelike.world.room import Room


@pytest.fixture
def large_room():
    """Create a large room for testing."""
    return Room(x=5, y=5, width=20, height=20)


def test_place_items_returns_list(large_room):
    """place_items returns a list."""
    items = place_items(large_room, max_items=5)

    assert isinstance(items, list)


def test_place_items_respects_max_items(large_room):
    """place_items respects max_items parameter."""
    items = place_items(large_room, max_items=3)

    assert len(items) <= 3


def test_place_items_spawns_items_in_room(large_room):
    """Items spawn within room boundaries."""
    items = place_items(large_room, max_items=10)

    for item in items:
        assert large_room.x < item.position.x < large_room.x2
        assert large_room.y < item.position.y < large_room.y2


def test_place_items_no_duplicate_positions(large_room):
    """No two items spawn at same position."""
    items = place_items(large_room, max_items=10)

    positions = [item.position for item in items]
    assert len(positions) == len(set(positions))


def test_all_item_types_can_spawn(large_room):
    """All item types can eventually spawn with repeated attempts."""
    # Set seed for reproducibility
    random.seed(42)

    # Spawn many items to ensure we hit all types
    spawned_types = set()
    for _ in range(1000):
        items = place_items(large_room, max_items=1)
        if items and hasattr(items[0], 'item_type'):
            spawned_types.add(items[0].item_type)

    # Verify we spawned a diverse set (at least 15 different types)
    assert len(spawned_types) >= 15


def test_rare_items_can_spawn(large_room):
    """Ultra-rare items like cursed ring can spawn."""
    # Set seed for reproducibility
    random.seed(12345)

    # Spawn many items to find rare ones
    spawned_types = set()
    for _ in range(2000):
        items = place_items(large_room, max_items=1)
        if items and hasattr(items[0], 'item_type'):
            spawned_types.add(items[0].item_type)

    # Check for some rare items that were previously broken
    rare_items = {
        ItemType.CHEESE_WHEEL,
        ItemType.LUCKY_COIN,
        ItemType.CURSED_RING,
        ItemType.GIGANTISM_POTION,
        ItemType.SHRINKING_POTION,
    }

    # At least some rare items should spawn
    assert len(spawned_types.intersection(rare_items)) > 0


def test_cursed_ring_can_spawn(large_room):
    """Cursed ring (ultra rare) can eventually spawn."""
    # Set seed for reproducibility
    random.seed(99999)

    # Try many times to spawn cursed ring
    found_cursed_ring = False
    for _ in range(5000):
        items = place_items(large_room, max_items=1)
        if items and hasattr(items[0], 'item_type') and items[0].item_type == ItemType.CURSED_RING:
            found_cursed_ring = True
            break

    assert found_cursed_ring


def test_weighted_distribution_favors_common_items(large_room):
    """Common items spawn more frequently than rare items."""
    # Set seed for reproducibility
    random.seed(555)

    # Count spawns
    item_counts = {}
    for _ in range(500):
        items = place_items(large_room, max_items=1)
        if items and hasattr(items[0], 'item_type'):
            item_type = items[0].item_type
            item_counts[item_type] = item_counts.get(item_type, 0) + 1

    # Healing potion (weight 30) should spawn more than cursed ring (weight 1)
    healing_count = item_counts.get(ItemType.HEALING_POTION, 0)
    cursed_count = item_counts.get(ItemType.CURSED_RING, 0)

    assert healing_count > cursed_count * 5  # At least 5x more common
