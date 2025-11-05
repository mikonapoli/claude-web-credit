"""Tests for item system."""

from roguelike.entities.item import Item, ItemType, create_healing_potion
from roguelike.utils.position import Position


def test_item_creation():
    """Item can be created."""
    item = Item(
        position=Position(5, 5),
        char="!",
        name="Test Item",
        item_type=ItemType.HEALING_POTION,
        value=10,
    )
    assert item.position == Position(5, 5)


def test_item_has_correct_char():
    """Item has correct display character."""
    item = Item(
        position=Position(5, 5),
        char="!",
        name="Test Item",
        item_type=ItemType.HEALING_POTION,
        value=10,
    )
    assert item.char == "!"


def test_item_has_correct_name():
    """Item has correct name."""
    item = Item(
        position=Position(5, 5),
        char="!",
        name="Test Item",
        item_type=ItemType.HEALING_POTION,
        value=10,
    )
    assert item.name == "Test Item"


def test_item_has_correct_type():
    """Item has correct item type."""
    item = Item(
        position=Position(5, 5),
        char="!",
        name="Test Item",
        item_type=ItemType.HEALING_POTION,
        value=10,
    )
    assert item.item_type == ItemType.HEALING_POTION


def test_item_has_correct_value():
    """Item has correct value."""
    item = Item(
        position=Position(5, 5),
        char="!",
        name="Test Item",
        item_type=ItemType.HEALING_POTION,
        value=10,
    )
    assert item.value == 10


def test_item_does_not_block_movement():
    """Item does not block movement."""
    item = Item(
        position=Position(5, 5),
        char="!",
        name="Test Item",
        item_type=ItemType.HEALING_POTION,
        value=10,
    )
    assert item.blocks_movement is False


def test_create_healing_potion_returns_item():
    """create_healing_potion returns an Item."""
    potion = create_healing_potion(Position(5, 5))
    assert isinstance(potion, Item)


def test_healing_potion_has_correct_position():
    """Healing potion has correct position."""
    potion = create_healing_potion(Position(5, 5))
    assert potion.position == Position(5, 5)


def test_healing_potion_has_correct_char():
    """Healing potion has correct display character."""
    potion = create_healing_potion(Position(5, 5))
    assert potion.char == "!"


def test_healing_potion_has_correct_name():
    """Healing potion has correct name."""
    potion = create_healing_potion(Position(5, 5))
    assert potion.name == "Healing Potion"


def test_healing_potion_has_correct_type():
    """Healing potion has correct item type."""
    potion = create_healing_potion(Position(5, 5))
    assert potion.item_type == ItemType.HEALING_POTION


def test_healing_potion_has_correct_value():
    """Healing potion has correct healing value."""
    potion = create_healing_potion(Position(5, 5))
    assert potion.value == 20


def test_healing_potion_does_not_block_movement():
    """Healing potion does not block movement."""
    potion = create_healing_potion(Position(5, 5))
    assert potion.blocks_movement is False
