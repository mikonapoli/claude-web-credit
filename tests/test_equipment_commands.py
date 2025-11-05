"""Tests for equipment commands."""

import pytest

from roguelike.commands.equipment_commands import EquipItemCommand, UnequipItemCommand
from roguelike.components.combat import CombatComponent
from roguelike.components.entity import ComponentEntity
from roguelike.components.equipment import EquipmentComponent, EquipmentSlot, EquipmentStats
from roguelike.components.health import HealthComponent
from roguelike.components.inventory import InventoryComponent
from roguelike.engine.events import EventBus
from roguelike.systems.equipment_system import EquipmentSystem
from roguelike.utils.position import Position


@pytest.fixture
def event_bus():
    """Create an event bus for testing."""
    return EventBus()


@pytest.fixture
def equipment_system(event_bus):
    """Create an equipment system for testing."""
    return EquipmentSystem(event_bus)


@pytest.fixture
def player_entity():
    """Create a player entity with all necessary components."""
    entity = ComponentEntity(
        position=Position(5, 5),
        char="@",
        name="Player",
        blocks_movement=True,
    )
    # Add components
    entity.add_component(EquipmentComponent())
    entity.add_component(CombatComponent(power=5, defense=2))
    entity.add_component(HealthComponent(max_hp=30))
    entity.add_component(InventoryComponent(capacity=10))
    return entity


@pytest.fixture
def iron_sword():
    """Create an iron sword item."""
    sword = ComponentEntity(
        position=Position(0, 0),
        char="/",
        name="Iron Sword",
        blocks_movement=False,
    )
    equipment_stats = EquipmentStats(
        slot=EquipmentSlot.WEAPON,
        power_bonus=3,
        defense_bonus=0,
    )
    sword.add_component(equipment_stats)
    return sword


@pytest.fixture
def steel_sword():
    """Create a steel sword item."""
    sword = ComponentEntity(
        position=Position(0, 0),
        char="/",
        name="Steel Sword",
        blocks_movement=False,
    )
    equipment_stats = EquipmentStats(
        slot=EquipmentSlot.WEAPON,
        power_bonus=5,
        defense_bonus=0,
    )
    sword.add_component(equipment_stats)
    return sword


@pytest.fixture
def leather_armor():
    """Create leather armor item."""
    armor = ComponentEntity(
        position=Position(0, 0),
        char="[",
        name="Leather Armor",
        blocks_movement=False,
    )
    equipment_stats = EquipmentStats(
        slot=EquipmentSlot.ARMOR,
        power_bonus=0,
        defense_bonus=2,
    )
    armor.add_component(equipment_stats)
    return armor


def test_equip_item_from_inventory(equipment_system, player_entity, iron_sword):
    """Equipping item from inventory succeeds."""
    inventory = player_entity.get_component(InventoryComponent)
    inventory.add_item(iron_sword)

    command = EquipItemCommand(player_entity, iron_sword, equipment_system)
    result = command.execute()

    assert result.success is True


def test_equip_item_consumes_turn(equipment_system, player_entity, iron_sword):
    """Equipping item consumes turn."""
    inventory = player_entity.get_component(InventoryComponent)
    inventory.add_item(iron_sword)

    command = EquipItemCommand(player_entity, iron_sword, equipment_system)
    result = command.execute()

    assert result.turn_consumed is True


def test_equip_item_removes_from_inventory(equipment_system, player_entity, iron_sword):
    """Equipping item removes it from inventory."""
    inventory = player_entity.get_component(InventoryComponent)
    inventory.add_item(iron_sword)

    command = EquipItemCommand(player_entity, iron_sword, equipment_system)
    command.execute()

    assert iron_sword not in inventory.get_items()


def test_equip_item_adds_to_equipment(equipment_system, player_entity, iron_sword):
    """Equipping item adds it to equipment slot."""
    inventory = player_entity.get_component(InventoryComponent)
    inventory.add_item(iron_sword)

    command = EquipItemCommand(player_entity, iron_sword, equipment_system)
    command.execute()

    equipment = player_entity.get_component(EquipmentComponent)
    assert equipment.get_equipped(EquipmentSlot.WEAPON) == iron_sword


def test_equip_item_not_in_inventory_fails(equipment_system, player_entity, iron_sword):
    """Equipping item not in inventory fails."""
    command = EquipItemCommand(player_entity, iron_sword, equipment_system)
    result = command.execute()

    assert result.success is False


def test_equip_item_without_equipment_component_fails(equipment_system, iron_sword):
    """Equipping item on entity without EquipmentComponent fails."""
    entity_no_equipment = ComponentEntity(Position(0, 0), "@", "Test", True)
    entity_no_equipment.add_component(InventoryComponent())
    inventory = entity_no_equipment.get_component(InventoryComponent)
    inventory.add_item(iron_sword)

    command = EquipItemCommand(entity_no_equipment, iron_sword, equipment_system)
    result = command.execute()

    assert result.success is False


def test_equip_item_without_equipment_stats_fails(equipment_system, player_entity):
    """Equipping item without EquipmentStats fails."""
    inventory = player_entity.get_component(InventoryComponent)
    invalid_item = ComponentEntity(Position(0, 0), "X", "Invalid", False)
    inventory.add_item(invalid_item)

    command = EquipItemCommand(player_entity, invalid_item, equipment_system)
    result = command.execute()

    assert result.success is False


def test_equip_replaces_previous_weapon_in_inventory(
    equipment_system, player_entity, iron_sword, steel_sword
):
    """Equipping new weapon puts old weapon back in inventory."""
    inventory = player_entity.get_component(InventoryComponent)
    inventory.add_item(iron_sword)
    inventory.add_item(steel_sword)

    # Equip iron sword
    command1 = EquipItemCommand(player_entity, iron_sword, equipment_system)
    command1.execute()

    # Equip steel sword (should replace iron sword)
    command2 = EquipItemCommand(player_entity, steel_sword, equipment_system)
    command2.execute()

    # Iron sword should be back in inventory
    assert iron_sword in inventory.get_items()


def test_equip_replaces_previous_weapon_in_equipment(
    equipment_system, player_entity, iron_sword, steel_sword
):
    """Equipping new weapon replaces old weapon in slot."""
    inventory = player_entity.get_component(InventoryComponent)
    inventory.add_item(iron_sword)
    inventory.add_item(steel_sword)

    # Equip iron sword
    command1 = EquipItemCommand(player_entity, iron_sword, equipment_system)
    command1.execute()

    # Equip steel sword
    command2 = EquipItemCommand(player_entity, steel_sword, equipment_system)
    command2.execute()

    equipment = player_entity.get_component(EquipmentComponent)
    assert equipment.get_equipped(EquipmentSlot.WEAPON) == steel_sword


def test_unequip_item_to_inventory(equipment_system, player_entity, iron_sword):
    """Unequipping item puts it in inventory."""
    inventory = player_entity.get_component(InventoryComponent)
    inventory.add_item(iron_sword)

    # Equip the item
    equip_command = EquipItemCommand(player_entity, iron_sword, equipment_system)
    equip_command.execute()

    # Unequip the item
    unequip_command = UnequipItemCommand(player_entity, EquipmentSlot.WEAPON, equipment_system)
    result = unequip_command.execute()

    assert result.success is True
    assert iron_sword in inventory.get_items()


def test_unequip_item_consumes_turn(equipment_system, player_entity, iron_sword):
    """Unequipping item consumes turn."""
    inventory = player_entity.get_component(InventoryComponent)
    inventory.add_item(iron_sword)

    # Equip the item
    equip_command = EquipItemCommand(player_entity, iron_sword, equipment_system)
    equip_command.execute()

    # Unequip the item
    unequip_command = UnequipItemCommand(player_entity, EquipmentSlot.WEAPON, equipment_system)
    result = unequip_command.execute()

    assert result.turn_consumed is True


def test_unequip_item_removes_from_equipment(equipment_system, player_entity, iron_sword):
    """Unequipping item removes it from equipment slot."""
    inventory = player_entity.get_component(InventoryComponent)
    inventory.add_item(iron_sword)

    # Equip the item
    equip_command = EquipItemCommand(player_entity, iron_sword, equipment_system)
    equip_command.execute()

    # Unequip the item
    unequip_command = UnequipItemCommand(player_entity, EquipmentSlot.WEAPON, equipment_system)
    unequip_command.execute()

    equipment = player_entity.get_component(EquipmentComponent)
    assert equipment.get_equipped(EquipmentSlot.WEAPON) is None


def test_unequip_empty_slot_fails(equipment_system, player_entity):
    """Unequipping empty slot fails."""
    command = UnequipItemCommand(player_entity, EquipmentSlot.WEAPON, equipment_system)
    result = command.execute()

    assert result.success is False


def test_unequip_with_full_inventory_fails(equipment_system, player_entity, iron_sword):
    """Unequipping item when inventory is full fails."""
    inventory = player_entity.get_component(InventoryComponent)

    # Fill inventory to capacity
    for i in range(inventory.capacity):
        dummy_item = ComponentEntity(Position(0, 0), "X", f"Dummy {i}", False)
        inventory.add_item(dummy_item)

    # Force equip an item (bypassing inventory check)
    equipment_system.equip_item(player_entity, iron_sword)

    # Try to unequip when inventory is full
    command = UnequipItemCommand(player_entity, EquipmentSlot.WEAPON, equipment_system)
    result = command.execute()

    assert result.success is False


def test_unequip_without_equipment_component_fails(equipment_system):
    """Unequipping from entity without EquipmentComponent fails."""
    entity_no_equipment = ComponentEntity(Position(0, 0), "@", "Test", True)
    entity_no_equipment.add_component(InventoryComponent())

    command = UnequipItemCommand(entity_no_equipment, EquipmentSlot.WEAPON, equipment_system)
    result = command.execute()

    assert result.success is False


def test_equip_and_unequip_maintains_stats(equipment_system, player_entity, iron_sword):
    """Equipping then unequipping maintains original stats."""
    combat = player_entity.get_component(CombatComponent)
    inventory = player_entity.get_component(InventoryComponent)
    inventory.add_item(iron_sword)

    initial_power = combat.power

    # Equip
    equip_command = EquipItemCommand(player_entity, iron_sword, equipment_system)
    equip_command.execute()

    # Unequip
    unequip_command = UnequipItemCommand(player_entity, EquipmentSlot.WEAPON, equipment_system)
    unequip_command.execute()

    assert combat.power == initial_power
