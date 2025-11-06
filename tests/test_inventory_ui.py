"""Tests for inventory UI."""

import pytest

from roguelike.entities.item import Item, ItemType, create_healing_potion
from roguelike.ui.inventory_ui import InventoryUI
from roguelike.utils.position import Position


@pytest.fixture
def inventory_ui():
    """Create an inventory UI for testing."""
    return InventoryUI(width=50, height=30)


@pytest.fixture
def sample_items():
    """Create sample items for testing."""
    return [
        create_healing_potion(Position(0, 0)),
        Item(Position(0, 0), "?", "Scroll of Fireball", ItemType.SCROLL_FIREBALL, 25),
        Item(Position(0, 0), "!", "Potion of Strength", ItemType.STRENGTH_POTION, 3),
    ]


def test_get_item_letters_maps_first_item_to_a(inventory_ui, sample_items):
    """First item is mapped to letter 'a'."""
    letter_map = inventory_ui.get_item_letters(sample_items)
    assert 'a' in letter_map


def test_get_item_letters_maps_second_item_to_b(inventory_ui, sample_items):
    """Second item is mapped to letter 'b'."""
    letter_map = inventory_ui.get_item_letters(sample_items)
    assert 'b' in letter_map


def test_get_item_letters_maps_third_item_to_c(inventory_ui, sample_items):
    """Third item is mapped to letter 'c'."""
    letter_map = inventory_ui.get_item_letters(sample_items)
    assert 'c' in letter_map


def test_get_item_letters_returns_correct_index_for_a(inventory_ui, sample_items):
    """Letter 'a' maps to index 0."""
    letter_map = inventory_ui.get_item_letters(sample_items)
    assert letter_map['a'] == 0


def test_get_item_letters_returns_correct_index_for_b(inventory_ui, sample_items):
    """Letter 'b' maps to index 1."""
    letter_map = inventory_ui.get_item_letters(sample_items)
    assert letter_map['b'] == 1


def test_get_item_letters_limits_to_26_items(inventory_ui):
    """Only first 26 items get letter mappings."""
    # Create 30 items
    items = [create_healing_potion(Position(0, 0)) for _ in range(30)]
    letter_map = inventory_ui.get_item_letters(items)
    assert len(letter_map) == 26


def test_get_item_by_letter_returns_correct_item(inventory_ui, sample_items):
    """Get item by letter 'a' returns first item."""
    item = inventory_ui.get_item_by_letter(sample_items, 'a')
    assert item == sample_items[0]


def test_get_item_by_letter_returns_none_for_invalid_letter(inventory_ui, sample_items):
    """Get item by invalid letter returns None."""
    item = inventory_ui.get_item_by_letter(sample_items, 'z')
    assert item is None


def test_get_display_lines_shows_empty_message_for_empty_inventory(inventory_ui):
    """Empty inventory shows appropriate message."""
    lines = inventory_ui.get_display_lines([])
    assert "empty" in lines[0].lower()


def test_get_display_lines_shows_item_with_letter(inventory_ui, sample_items):
    """Display lines show items with letter prefix."""
    lines = inventory_ui.get_display_lines(sample_items)
    assert "(a)" in lines[0]


def test_get_display_lines_shows_item_name(inventory_ui, sample_items):
    """Display lines show item names."""
    lines = inventory_ui.get_display_lines(sample_items)
    assert "Healing Potion" in lines[0]


def test_get_display_lines_shows_all_items(inventory_ui, sample_items):
    """Display lines include all items."""
    lines = inventory_ui.get_display_lines(sample_items)
    assert len(lines) == 3


def test_calculate_position_centers_horizontally(inventory_ui):
    """Position is centered horizontally on screen."""
    x, y = inventory_ui.calculate_position(80, 50)
    assert x == (80 - 50) // 2


def test_calculate_position_centers_vertically(inventory_ui):
    """Position is centered vertically on screen."""
    x, y = inventory_ui.calculate_position(80, 50)
    assert y == (50 - 30) // 2
