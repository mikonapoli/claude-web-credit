"""Tests for inventory menu commands."""

import pytest

from roguelike.commands.inventory_menu_commands import (
    OpenInventoryMenuCommand,
    CloseInventoryMenuCommand,
    NavigateInventoryCommand,
    SetInventoryModeCommand,
    ExamineItemCommand,
)
from roguelike.components.entity import ComponentEntity
from roguelike.components.health import HealthComponent
from roguelike.components.inventory import InventoryComponent
from roguelike.entities.item import create_healing_potion
from roguelike.ui.inventory_menu import InventoryMenu
from roguelike.ui.message_log import MessageLog
from roguelike.utils.position import Position


@pytest.fixture
def player():
    """Create a test player with inventory."""
    player = ComponentEntity(Position(0, 0), "@", "Player")
    player.add_component(HealthComponent(max_hp=100))
    player.add_component(InventoryComponent(capacity=26))
    return player


@pytest.fixture
def inventory_menu():
    """Create a test inventory menu."""
    return InventoryMenu()


@pytest.fixture
def message_log():
    """Create a test message log."""
    return MessageLog()


def test_open_inventory_menu_command(player, inventory_menu, message_log):
    """Open inventory menu command opens the menu."""
    # Add some items to player inventory
    inventory = player.get_component(InventoryComponent)
    item = create_healing_potion(Position(0, 0))
    inventory.add_item(item)

    cmd = OpenInventoryMenuCommand(player, inventory_menu, message_log)
    result = cmd.execute()

    assert result.success is True
    assert result.turn_consumed is False
    assert inventory_menu.is_open is True
    assert len(inventory_menu.items) == 1
    assert result.data.get("inventory_menu_opened") is True


def test_open_inventory_menu_without_inventory_component(inventory_menu, message_log):
    """Open inventory menu without inventory component fails."""
    player = ComponentEntity(Position(0, 0), "@", "Player")

    cmd = OpenInventoryMenuCommand(player, inventory_menu, message_log)
    result = cmd.execute()

    assert result.success is False
    assert result.turn_consumed is False
    assert inventory_menu.is_open is False


def test_close_inventory_menu_command(inventory_menu):
    """Close inventory menu command closes the menu."""
    # Open menu first
    items = [create_healing_potion(Position(0, 0))]
    inventory_menu.open(items)

    cmd = CloseInventoryMenuCommand(inventory_menu)
    result = cmd.execute()

    assert result.success is True
    assert result.turn_consumed is False
    assert inventory_menu.is_open is False
    assert result.data.get("inventory_menu_closed") is True


def test_navigate_inventory_up(inventory_menu):
    """Navigate inventory up selects previous item."""
    items = [
        create_healing_potion(Position(0, 0)),
        create_healing_potion(Position(0, 0)),
        create_healing_potion(Position(0, 0)),
    ]
    inventory_menu.open(items)
    inventory_menu.selected_index = 1

    cmd = NavigateInventoryCommand(inventory_menu, "up")
    result = cmd.execute()

    assert result.success is True
    assert result.turn_consumed is False
    assert inventory_menu.selected_index == 0


def test_navigate_inventory_down(inventory_menu):
    """Navigate inventory down selects next item."""
    items = [
        create_healing_potion(Position(0, 0)),
        create_healing_potion(Position(0, 0)),
        create_healing_potion(Position(0, 0)),
    ]
    inventory_menu.open(items)
    inventory_menu.selected_index = 0

    cmd = NavigateInventoryCommand(inventory_menu, "down")
    result = cmd.execute()

    assert result.success is True
    assert result.turn_consumed is False
    assert inventory_menu.selected_index == 1


def test_set_inventory_mode_use(inventory_menu):
    """Set inventory mode to use."""
    inventory_menu.mode = "drop"

    cmd = SetInventoryModeCommand(inventory_menu, "use")
    result = cmd.execute()

    assert result.success is True
    assert result.turn_consumed is False
    assert inventory_menu.mode == "use"


def test_set_inventory_mode_drop(inventory_menu):
    """Set inventory mode to drop."""
    cmd = SetInventoryModeCommand(inventory_menu, "drop")
    result = cmd.execute()

    assert result.success is True
    assert result.turn_consumed is False
    assert inventory_menu.mode == "drop"


def test_set_inventory_mode_examine(inventory_menu):
    """Set inventory mode to examine."""
    cmd = SetInventoryModeCommand(inventory_menu, "examine")
    result = cmd.execute()

    assert result.success is True
    assert result.turn_consumed is False
    assert inventory_menu.mode == "examine"


def test_examine_item_command(inventory_menu, message_log):
    """Examine item command returns item description."""
    items = [create_healing_potion(Position(0, 0))]
    inventory_menu.open(items)

    cmd = ExamineItemCommand(inventory_menu, message_log)
    result = cmd.execute()

    assert result.success is True
    assert result.turn_consumed is False
    assert result.data.get("examine_item") is True
    assert result.data.get("item") is not None
    assert result.data.get("description_lines") is not None
    assert len(result.data.get("description_lines")) > 0


def test_examine_item_command_no_selection(inventory_menu, message_log):
    """Examine item command with no selection fails."""
    inventory_menu.open([])

    cmd = ExamineItemCommand(inventory_menu, message_log)
    result = cmd.execute()

    assert result.success is False
    assert result.turn_consumed is False
