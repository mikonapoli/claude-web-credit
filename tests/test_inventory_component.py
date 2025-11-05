"""Tests for InventoryComponent."""

from roguelike.components.entity import ComponentEntity
from roguelike.components.inventory import InventoryComponent
from roguelike.entities.item import create_healing_potion
from roguelike.utils.position import Position


def test_inventory_component_creation():
    """InventoryComponent can be created."""
    inventory_comp = InventoryComponent(capacity=26)
    assert inventory_comp.capacity == 26


def test_inventory_component_creation_with_custom_capacity():
    """InventoryComponent can be created with custom capacity."""
    inventory_comp = InventoryComponent(capacity=10)
    assert inventory_comp.capacity == 10


def test_add_inventory_component_to_entity():
    """Can add InventoryComponent to entity."""
    entity = ComponentEntity(Position(5, 5), "@", "Player")
    inventory_comp = InventoryComponent(capacity=26)
    entity.add_component(inventory_comp)

    assert entity.has_component(InventoryComponent)


def test_get_inventory_component_from_entity():
    """Can retrieve InventoryComponent from entity."""
    entity = ComponentEntity(Position(5, 5), "@", "Player")
    inventory_comp = InventoryComponent(capacity=26)
    entity.add_component(inventory_comp)

    retrieved = entity.get_component(InventoryComponent)
    assert retrieved is inventory_comp


def test_inventory_component_starts_empty():
    """InventoryComponent starts with no items."""
    inventory_comp = InventoryComponent(capacity=26)
    assert len(inventory_comp) == 0


def test_inventory_component_add_item():
    """Can add item to InventoryComponent."""
    inventory_comp = InventoryComponent(capacity=26)
    item = create_healing_potion(Position(0, 0))

    result = inventory_comp.add_item(item)
    assert result is True


def test_inventory_component_add_item_increases_count():
    """Adding item to InventoryComponent increases count."""
    inventory_comp = InventoryComponent(capacity=26)
    item = create_healing_potion(Position(0, 0))

    inventory_comp.add_item(item)
    assert len(inventory_comp) == 1


def test_inventory_component_cannot_add_when_full():
    """Cannot add item when InventoryComponent is full."""
    inventory_comp = InventoryComponent(capacity=1)
    item1 = create_healing_potion(Position(0, 0))
    item2 = create_healing_potion(Position(1, 1))

    inventory_comp.add_item(item1)
    result = inventory_comp.add_item(item2)
    assert result is False


def test_inventory_component_is_full():
    """InventoryComponent is_full returns True when at capacity."""
    inventory_comp = InventoryComponent(capacity=1)
    item = create_healing_potion(Position(0, 0))

    inventory_comp.add_item(item)
    assert inventory_comp.is_full() is True


def test_inventory_component_remove_item():
    """Can remove item from InventoryComponent."""
    inventory_comp = InventoryComponent(capacity=26)
    item = create_healing_potion(Position(0, 0))

    inventory_comp.add_item(item)
    result = inventory_comp.remove_item(item)
    assert result is True


def test_inventory_component_remove_item_decreases_count():
    """Removing item from InventoryComponent decreases count."""
    inventory_comp = InventoryComponent(capacity=26)
    item = create_healing_potion(Position(0, 0))

    inventory_comp.add_item(item)
    inventory_comp.remove_item(item)
    assert len(inventory_comp) == 0


def test_inventory_component_get_item_by_index():
    """Can get item by index from InventoryComponent."""
    inventory_comp = InventoryComponent(capacity=26)
    item = create_healing_potion(Position(0, 0))

    inventory_comp.add_item(item)
    retrieved = inventory_comp.get_item_by_index(0)
    assert retrieved is item


def test_inventory_component_get_items():
    """Can get all items from InventoryComponent."""
    inventory_comp = InventoryComponent(capacity=26)
    item1 = create_healing_potion(Position(0, 0))
    item2 = create_healing_potion(Position(1, 1))

    inventory_comp.add_item(item1)
    inventory_comp.add_item(item2)
    items = inventory_comp.get_items()
    assert len(items) == 2


def test_inventory_component_get_items_contains_added_items():
    """get_items contains all added items."""
    inventory_comp = InventoryComponent(capacity=26)
    item1 = create_healing_potion(Position(0, 0))
    item2 = create_healing_potion(Position(1, 1))

    inventory_comp.add_item(item1)
    inventory_comp.add_item(item2)
    items = inventory_comp.get_items()
    assert item1 in items and item2 in items
