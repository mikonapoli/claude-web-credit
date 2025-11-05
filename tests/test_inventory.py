"""Tests for inventory system."""

from roguelike.entities.item import Item, ItemType, create_healing_potion
from roguelike.systems.inventory import Inventory
from roguelike.utils.position import Position


def test_inventory_creation():
    """Inventory can be created with default capacity."""
    inventory = Inventory()
    assert inventory.capacity == 26


def test_inventory_creation_with_custom_capacity():
    """Inventory can be created with custom capacity."""
    inventory = Inventory(capacity=10)
    assert inventory.capacity == 10


def test_inventory_starts_empty():
    """Inventory starts with no items."""
    inventory = Inventory()
    assert len(inventory) == 0


def test_add_item_to_inventory():
    """Can add item to inventory."""
    inventory = Inventory()
    item = create_healing_potion(Position(0, 0))

    result = inventory.add(item)
    assert result is True


def test_add_item_increases_count():
    """Adding item increases inventory count."""
    inventory = Inventory()
    item = create_healing_potion(Position(0, 0))

    inventory.add(item)
    assert len(inventory) == 1


def test_add_multiple_items():
    """Can add multiple items to inventory."""
    inventory = Inventory()
    item1 = create_healing_potion(Position(0, 0))
    item2 = create_healing_potion(Position(1, 1))

    inventory.add(item1)
    inventory.add(item2)
    assert len(inventory) == 2


def test_cannot_add_item_when_full():
    """Cannot add item when inventory is at capacity."""
    inventory = Inventory(capacity=1)
    item1 = create_healing_potion(Position(0, 0))
    item2 = create_healing_potion(Position(1, 1))

    inventory.add(item1)
    result = inventory.add(item2)
    assert result is False


def test_inventory_count_unchanged_when_add_fails():
    """Inventory count unchanged when add fails."""
    inventory = Inventory(capacity=1)
    item1 = create_healing_potion(Position(0, 0))
    item2 = create_healing_potion(Position(1, 1))

    inventory.add(item1)
    inventory.add(item2)
    assert len(inventory) == 1


def test_is_full_returns_false_when_not_full():
    """is_full returns False when inventory has space."""
    inventory = Inventory(capacity=2)
    item = create_healing_potion(Position(0, 0))

    inventory.add(item)
    assert inventory.is_full() is False


def test_is_full_returns_true_when_full():
    """is_full returns True when inventory is at capacity."""
    inventory = Inventory(capacity=1)
    item = create_healing_potion(Position(0, 0))

    inventory.add(item)
    assert inventory.is_full() is True


def test_remove_item_from_inventory():
    """Can remove item from inventory."""
    inventory = Inventory()
    item = create_healing_potion(Position(0, 0))

    inventory.add(item)
    result = inventory.remove(item)
    assert result is True


def test_remove_item_decreases_count():
    """Removing item decreases inventory count."""
    inventory = Inventory()
    item = create_healing_potion(Position(0, 0))

    inventory.add(item)
    inventory.remove(item)
    assert len(inventory) == 0


def test_remove_nonexistent_item_returns_false():
    """Removing nonexistent item returns False."""
    inventory = Inventory()
    item = create_healing_potion(Position(0, 0))

    result = inventory.remove(item)
    assert result is False


def test_remove_nonexistent_item_count_unchanged():
    """Inventory count unchanged when removing nonexistent item."""
    inventory = Inventory()
    item1 = create_healing_potion(Position(0, 0))
    item2 = create_healing_potion(Position(1, 1))

    inventory.add(item1)
    inventory.remove(item2)
    assert len(inventory) == 1


def test_get_item_by_valid_index():
    """Can get item by valid index."""
    inventory = Inventory()
    item = create_healing_potion(Position(0, 0))

    inventory.add(item)
    retrieved = inventory.get_item_by_index(0)
    assert retrieved is item


def test_get_item_by_invalid_index_returns_none():
    """Getting item by invalid index returns None."""
    inventory = Inventory()

    retrieved = inventory.get_item_by_index(0)
    assert retrieved is None


def test_get_item_by_negative_index_returns_none():
    """Getting item by negative index returns None."""
    inventory = Inventory()
    item = create_healing_potion(Position(0, 0))

    inventory.add(item)
    retrieved = inventory.get_item_by_index(-1)
    assert retrieved is None


def test_get_item_by_out_of_bounds_index():
    """Getting item by out of bounds index returns None."""
    inventory = Inventory()
    item = create_healing_potion(Position(0, 0))

    inventory.add(item)
    retrieved = inventory.get_item_by_index(1)
    assert retrieved is None
