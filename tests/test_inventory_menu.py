"""Tests for inventory menu UI."""

import pytest

from roguelike.entities.item import Item, ItemType, create_healing_potion
from roguelike.ui.inventory_menu import InventoryMenu
from roguelike.utils.position import Position


def test_inventory_menu_initial_state():
    """Inventory menu starts closed."""
    menu = InventoryMenu()
    assert menu.is_open is False
    assert len(menu.items) == 0
    assert menu.selected_index == 0
    assert menu.mode == "use"


def test_open_inventory_menu():
    """Opening inventory menu sets items and opens menu."""
    menu = InventoryMenu()
    items = [
        create_healing_potion(Position(0, 0)),
        create_healing_potion(Position(0, 0)),
    ]

    menu.open(items)

    assert menu.is_open is True
    assert len(menu.items) == 2
    assert menu.selected_index == 0


def test_open_empty_inventory():
    """Opening menu with empty inventory."""
    menu = InventoryMenu()
    menu.open([])

    assert menu.is_open is True
    assert len(menu.items) == 0
    assert menu.selected_index == 0


def test_close_inventory_menu():
    """Closing inventory menu resets state."""
    menu = InventoryMenu()
    items = [create_healing_potion(Position(0, 0))]
    menu.open(items)
    menu.close()

    assert menu.is_open is False
    assert len(menu.items) == 0
    assert menu.selected_index == 0
    assert menu.mode == "use"


def test_select_next_item():
    """Selecting next item increments index."""
    menu = InventoryMenu()
    items = [
        create_healing_potion(Position(0, 0)),
        create_healing_potion(Position(0, 0)),
        create_healing_potion(Position(0, 0)),
    ]
    menu.open(items)

    menu.select_next()
    assert menu.selected_index == 1

    menu.select_next()
    assert menu.selected_index == 2


def test_select_next_wraps_around():
    """Selecting next at end wraps to start."""
    menu = InventoryMenu()
    items = [
        create_healing_potion(Position(0, 0)),
        create_healing_potion(Position(0, 0)),
    ]
    menu.open(items)

    menu.selected_index = 1
    menu.select_next()

    assert menu.selected_index == 0


def test_select_previous_item():
    """Selecting previous item decrements index."""
    menu = InventoryMenu()
    items = [
        create_healing_potion(Position(0, 0)),
        create_healing_potion(Position(0, 0)),
        create_healing_potion(Position(0, 0)),
    ]
    menu.open(items)
    menu.selected_index = 2

    menu.select_previous()
    assert menu.selected_index == 1

    menu.select_previous()
    assert menu.selected_index == 0


def test_select_previous_wraps_around():
    """Selecting previous at start wraps to end."""
    menu = InventoryMenu()
    items = [
        create_healing_potion(Position(0, 0)),
        create_healing_potion(Position(0, 0)),
    ]
    menu.open(items)

    menu.select_previous()

    assert menu.selected_index == 1


def test_set_mode():
    """Setting mode changes the mode."""
    menu = InventoryMenu()

    menu.set_mode("drop")
    assert menu.mode == "drop"

    menu.set_mode("examine")
    assert menu.mode == "examine"

    menu.set_mode("use")
    assert menu.mode == "use"


def test_set_invalid_mode():
    """Setting invalid mode does not change mode."""
    menu = InventoryMenu()

    menu.set_mode("invalid")
    assert menu.mode == "use"


def test_get_selected_item():
    """Getting selected item returns correct item."""
    menu = InventoryMenu()
    items = [
        create_healing_potion(Position(0, 0)),
        Item(Position(0, 0), "!", "Potion", ItemType.HEALING_POTION, 30),
    ]
    menu.open(items)

    menu.selected_index = 0
    selected = menu.get_selected_item()
    assert selected == items[0]

    menu.selected_index = 1
    selected = menu.get_selected_item()
    assert selected == items[1]


def test_get_selected_item_when_closed():
    """Getting selected item when menu is closed returns None."""
    menu = InventoryMenu()
    items = [create_healing_potion(Position(0, 0))]
    menu.open(items)
    menu.close()

    selected = menu.get_selected_item()
    assert selected is None


def test_get_selected_item_with_empty_inventory():
    """Getting selected item with empty inventory returns None."""
    menu = InventoryMenu()
    menu.open([])

    selected = menu.get_selected_item()
    assert selected is None


def test_get_menu_lines_with_items():
    """Getting menu lines shows items correctly."""
    menu = InventoryMenu()
    items = [
        Item(Position(0, 0), "!", "Healing Potion", ItemType.HEALING_POTION, 20),
        Item(Position(0, 0), "!", "Greater Healing Potion", ItemType.GREATER_HEALING_POTION, 40),
    ]
    menu.open(items)

    lines = menu.get_menu_lines(capacity=26)

    assert "=== INVENTORY ===" in lines
    assert "Items: 2/26" in lines
    assert any("Healing Potion" in line for line in lines)
    assert any("Greater Healing Potion" in line for line in lines)


def test_get_menu_lines_shows_selection():
    """Getting menu lines highlights selected item."""
    menu = InventoryMenu()
    items = [
        Item(Position(0, 0), "!", "Potion A", ItemType.HEALING_POTION, 20),
        Item(Position(0, 0), "!", "Potion B", ItemType.HEALING_POTION, 20),
    ]
    menu.open(items)
    menu.selected_index = 1

    lines = menu.get_menu_lines(capacity=26)

    # Find the line with "Potion B" - it should have ">" prefix
    potion_b_lines = [line for line in lines if "Potion B" in line]
    assert len(potion_b_lines) > 0
    assert potion_b_lines[0].strip().startswith(">")


def test_get_menu_lines_empty_inventory():
    """Getting menu lines with empty inventory shows empty message."""
    menu = InventoryMenu()
    menu.open([])

    lines = menu.get_menu_lines(capacity=26)

    assert "=== INVENTORY ===" in lines
    assert "Items: 0/26" in lines
    assert any("(empty)" in line for line in lines)


def test_get_menu_lines_shows_mode():
    """Getting menu lines displays current mode."""
    menu = InventoryMenu()
    items = [create_healing_potion(Position(0, 0))]
    menu.open(items)

    menu.set_mode("use")
    lines = menu.get_menu_lines(capacity=26)
    assert any("Mode: USE" in line for line in lines)

    menu.set_mode("drop")
    lines = menu.get_menu_lines(capacity=26)
    assert any("Mode: DROP" in line for line in lines)

    menu.set_mode("examine")
    lines = menu.get_menu_lines(capacity=26)
    assert any("Mode: EXAMINE" in line for line in lines)


def test_get_item_description():
    """Getting item description returns correct lines."""
    menu = InventoryMenu()
    item = Item(
        Position(0, 0),
        "!",
        "Healing Potion",
        ItemType.HEALING_POTION,
        20
    )

    description = menu.get_item_description(item)

    assert any("HEALING POTION" in line for line in description)
    assert any("Type:" in line for line in description)
    assert any("Effect Value:" in line for line in description)


def test_get_item_description_for_targeted_item():
    """Getting item description shows targeting requirement."""
    menu = InventoryMenu()
    item = Item(
        Position(0, 0),
        "?",
        "Scroll of Confusion",
        ItemType.SCROLL_CONFUSION,
        10
    )

    description = menu.get_item_description(item)

    assert any("Requires Target: Yes" in line for line in description)
