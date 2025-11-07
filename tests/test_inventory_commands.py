"""Tests for inventory commands."""

from typing import List

from roguelike.commands.inventory_commands import (
    DropItemCommand,
    PickupItemCommand,
    UseItemCommand,
)
from roguelike.components.entity import ComponentEntity
from roguelike.components.health import HealthComponent
from roguelike.components.inventory import InventoryComponent
from roguelike.entities.entity import Entity
from roguelike.entities.item import ItemType, create_healing_potion
from roguelike.utils.position import Position


def test_pickup_command_success():
    """PickupItemCommand successfully picks up item."""
    player = ComponentEntity(Position(5, 5), "@", "Player")
    inventory = InventoryComponent(capacity=26)
    player.add_component(inventory)

    item = create_healing_potion(Position(5, 5))
    entities: List[Entity] = [player, item]

    cmd = PickupItemCommand(player, entities)
    result = cmd.execute()

    assert result.success is True


def test_pickup_command_consumes_turn():
    """PickupItemCommand consumes a turn."""
    player = ComponentEntity(Position(5, 5), "@", "Player")
    inventory = InventoryComponent(capacity=26)
    player.add_component(inventory)

    item = create_healing_potion(Position(5, 5))
    entities: List[Entity] = [player, item]

    cmd = PickupItemCommand(player, entities)
    result = cmd.execute()

    assert result.turn_consumed is True


def test_pickup_command_adds_item_to_inventory():
    """PickupItemCommand adds item to player inventory."""
    player = ComponentEntity(Position(5, 5), "@", "Player")
    inventory = InventoryComponent(capacity=26)
    player.add_component(inventory)

    item = create_healing_potion(Position(5, 5))
    entities: List[Entity] = [player, item]

    cmd = PickupItemCommand(player, entities)
    cmd.execute()

    assert len(inventory) == 1


def test_pickup_command_removes_item_from_entities():
    """PickupItemCommand removes item from entities list."""
    player = ComponentEntity(Position(5, 5), "@", "Player")
    inventory = InventoryComponent(capacity=26)
    player.add_component(inventory)

    item = create_healing_potion(Position(5, 5))
    entities: List[Entity] = [player, item]

    cmd = PickupItemCommand(player, entities)
    cmd.execute()

    assert item not in entities


def test_pickup_command_no_item_at_position():
    """PickupItemCommand fails when no item at position."""
    player = ComponentEntity(Position(5, 5), "@", "Player")
    inventory = InventoryComponent(capacity=26)
    player.add_component(inventory)

    item = create_healing_potion(Position(10, 10))
    entities: List[Entity] = [player, item]

    cmd = PickupItemCommand(player, entities)
    result = cmd.execute()

    assert result.success is False


def test_pickup_command_no_item_turn_not_consumed():
    """PickupItemCommand doesn't consume turn when no item."""
    player = ComponentEntity(Position(5, 5), "@", "Player")
    inventory = InventoryComponent(capacity=26)
    player.add_component(inventory)

    item = create_healing_potion(Position(10, 10))
    entities: List[Entity] = [player, item]

    cmd = PickupItemCommand(player, entities)
    result = cmd.execute()

    assert result.turn_consumed is False


def test_pickup_command_inventory_full():
    """PickupItemCommand fails when inventory is full."""
    player = ComponentEntity(Position(5, 5), "@", "Player")
    inventory = InventoryComponent(capacity=0)
    player.add_component(inventory)

    item = create_healing_potion(Position(5, 5))
    entities: List[Entity] = [player, item]

    cmd = PickupItemCommand(player, entities)
    result = cmd.execute()

    assert result.success is False


def test_pickup_command_inventory_full_turn_not_consumed():
    """PickupItemCommand doesn't consume turn when inventory full."""
    player = ComponentEntity(Position(5, 5), "@", "Player")
    inventory = InventoryComponent(capacity=0)
    player.add_component(inventory)

    item = create_healing_potion(Position(5, 5))
    entities: List[Entity] = [player, item]

    cmd = PickupItemCommand(player, entities)
    result = cmd.execute()

    assert result.turn_consumed is False


def test_pickup_command_no_inventory_component():
    """PickupItemCommand fails when player has no inventory."""
    player = ComponentEntity(Position(5, 5), "@", "Player")

    item = create_healing_potion(Position(5, 5))
    entities: List[Entity] = [player, item]

    cmd = PickupItemCommand(player, entities)
    result = cmd.execute()

    assert result.success is False


def test_drop_command_success():
    """DropItemCommand successfully drops item."""
    player = ComponentEntity(Position(5, 5), "@", "Player")
    inventory = InventoryComponent(capacity=26)
    player.add_component(inventory)

    item = create_healing_potion(Position(5, 5))
    inventory.add_item(item)
    entities: List[Entity] = [player]

    cmd = DropItemCommand(player, item, entities)
    result = cmd.execute()

    assert result.success is True


def test_drop_command_consumes_turn():
    """DropItemCommand consumes a turn."""
    player = ComponentEntity(Position(5, 5), "@", "Player")
    inventory = InventoryComponent(capacity=26)
    player.add_component(inventory)

    item = create_healing_potion(Position(5, 5))
    inventory.add_item(item)
    entities: List[Entity] = [player]

    cmd = DropItemCommand(player, item, entities)
    result = cmd.execute()

    assert result.turn_consumed is True


def test_drop_command_removes_item_from_inventory():
    """DropItemCommand removes item from inventory."""
    player = ComponentEntity(Position(5, 5), "@", "Player")
    inventory = InventoryComponent(capacity=26)
    player.add_component(inventory)

    item = create_healing_potion(Position(5, 5))
    inventory.add_item(item)
    entities: List[Entity] = [player]

    cmd = DropItemCommand(player, item, entities)
    cmd.execute()

    assert len(inventory) == 0


def test_drop_command_adds_item_to_entities():
    """DropItemCommand adds item to entities list."""
    player = ComponentEntity(Position(5, 5), "@", "Player")
    inventory = InventoryComponent(capacity=26)
    player.add_component(inventory)

    item = create_healing_potion(Position(5, 5))
    inventory.add_item(item)
    entities: List[Entity] = [player]

    cmd = DropItemCommand(player, item, entities)
    cmd.execute()

    assert item in entities


def test_drop_command_sets_item_position():
    """DropItemCommand sets item position to player position."""
    player = ComponentEntity(Position(5, 5), "@", "Player")
    inventory = InventoryComponent(capacity=26)
    player.add_component(inventory)

    item = create_healing_potion(Position(0, 0))
    inventory.add_item(item)
    entities: List[Entity] = [player]

    cmd = DropItemCommand(player, item, entities)
    cmd.execute()

    assert item.position == Position(5, 5)


def test_drop_command_no_inventory_component():
    """DropItemCommand fails when player has no inventory."""
    player = ComponentEntity(Position(5, 5), "@", "Player")

    item = create_healing_potion(Position(5, 5))
    entities: List[Entity] = [player]

    cmd = DropItemCommand(player, item, entities)
    result = cmd.execute()

    assert result.success is False


def test_drop_command_item_not_in_inventory():
    """DropItemCommand fails when item not in inventory."""
    player = ComponentEntity(Position(5, 5), "@", "Player")
    inventory = InventoryComponent(capacity=26)
    player.add_component(inventory)

    item = create_healing_potion(Position(5, 5))
    entities: List[Entity] = [player]

    cmd = DropItemCommand(player, item, entities)
    result = cmd.execute()

    assert result.success is False


def test_use_item_command_success():
    """UseItemCommand successfully uses item."""
    player = ComponentEntity(Position(5, 5), "@", "Player")
    health = HealthComponent(max_hp=30)
    health.take_damage(10)
    player.add_component(health)
    inventory = InventoryComponent(capacity=26)
    player.add_component(inventory)

    item = create_healing_potion(Position(5, 5))
    inventory.add_item(item)

    cmd = UseItemCommand(player, item)
    result = cmd.execute()

    assert result.success is True


def test_use_item_command_consumes_turn():
    """UseItemCommand consumes a turn."""
    player = ComponentEntity(Position(5, 5), "@", "Player")
    health = HealthComponent(max_hp=30)
    health.take_damage(10)
    player.add_component(health)
    inventory = InventoryComponent(capacity=26)
    player.add_component(inventory)

    item = create_healing_potion(Position(5, 5))
    inventory.add_item(item)

    cmd = UseItemCommand(player, item)
    result = cmd.execute()

    assert result.turn_consumed is True


def test_use_item_command_removes_item_from_inventory():
    """UseItemCommand removes item from inventory."""
    player = ComponentEntity(Position(5, 5), "@", "Player")
    health = HealthComponent(max_hp=30)
    health.take_damage(10)
    player.add_component(health)
    inventory = InventoryComponent(capacity=26)
    player.add_component(inventory)

    item = create_healing_potion(Position(5, 5))
    inventory.add_item(item)

    cmd = UseItemCommand(player, item)
    cmd.execute()

    assert len(inventory) == 0


def test_use_healing_potion_heals_player():
    """Using healing potion heals player."""
    player = ComponentEntity(Position(5, 5), "@", "Player")
    health = HealthComponent(max_hp=30)
    health.take_damage(10)
    player.add_component(health)
    inventory = InventoryComponent(capacity=26)
    player.add_component(inventory)

    item = create_healing_potion(Position(5, 5))
    inventory.add_item(item)

    cmd = UseItemCommand(player, item)
    cmd.execute()

    assert health.hp > 20


def test_use_item_command_no_inventory():
    """UseItemCommand fails when player has no inventory."""
    player = ComponentEntity(Position(5, 5), "@", "Player")
    health = HealthComponent(max_hp=30)
    player.add_component(health)

    item = create_healing_potion(Position(5, 5))

    cmd = UseItemCommand(player, item)
    result = cmd.execute()

    assert result.success is False


def test_use_item_command_item_not_in_inventory():
    """UseItemCommand fails when item not in inventory."""
    player = ComponentEntity(Position(5, 5), "@", "Player")
    health = HealthComponent(max_hp=30)
    player.add_component(health)
    inventory = InventoryComponent(capacity=26)
    player.add_component(inventory)

    item = create_healing_potion(Position(5, 5))

    cmd = UseItemCommand(player, item)
    result = cmd.execute()

    assert result.success is False


def test_use_item_command_no_health_component():
    """UseItemCommand fails when player has no health component."""
    player = ComponentEntity(Position(5, 5), "@", "Player")
    inventory = InventoryComponent(capacity=26)
    player.add_component(inventory)

    item = create_healing_potion(Position(5, 5))
    inventory.add_item(item)

    cmd = UseItemCommand(player, item)
    result = cmd.execute()

    assert result.success is False


def test_use_healing_potion_at_full_health():
    """Using healing potion at full health fails (doesn't waste the potion)."""
    player = ComponentEntity(Position(5, 5), "@", "Player")
    health = HealthComponent(max_hp=30)
    player.add_component(health)
    inventory = InventoryComponent(capacity=26)
    player.add_component(inventory)

    item = create_healing_potion(Position(5, 5))
    inventory.add_item(item)

    cmd = UseItemCommand(player, item)
    result = cmd.execute()

    # Should fail because player is at full health - don't waste the potion
    assert result.success is False
    # Item should still be in inventory
    assert item in inventory.get_items()
