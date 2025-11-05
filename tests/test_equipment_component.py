"""Tests for equipment component."""

import pytest

from roguelike.components.entity import ComponentEntity
from roguelike.components.equipment import EquipmentComponent, EquipmentSlot, EquipmentStats
from roguelike.utils.position import Position


@pytest.fixture
def player_entity():
    """Create a player entity for testing."""
    entity = ComponentEntity(
        position=Position(5, 5),
        char="@",
        name="Player",
        blocks_movement=True,
    )
    equipment_comp = EquipmentComponent()
    entity.add_component(equipment_comp)
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


@pytest.fixture
def steel_helmet():
    """Create steel helmet item."""
    helmet = ComponentEntity(
        position=Position(0, 0),
        char="^",
        name="Steel Helmet",
        blocks_movement=False,
    )
    equipment_stats = EquipmentStats(
        slot=EquipmentSlot.HELMET,
        power_bonus=0,
        defense_bonus=1,
        max_hp_bonus=5,
    )
    helmet.add_component(equipment_stats)
    return helmet


def test_equipment_component_initializes_empty():
    """Equipment component starts with empty slots."""
    equipment = EquipmentComponent()
    assert len(equipment.get_all_equipped()) == 0


def test_equip_weapon_to_empty_slot(player_entity, iron_sword):
    """Equipping weapon to empty slot succeeds."""
    equipment = player_entity.get_component(EquipmentComponent)
    previous = equipment.equip(iron_sword)
    assert previous is None


def test_equip_weapon_updates_slot(player_entity, iron_sword):
    """Equipping weapon updates the weapon slot."""
    equipment = player_entity.get_component(EquipmentComponent)
    equipment.equip(iron_sword)
    assert equipment.get_equipped(EquipmentSlot.WEAPON) == iron_sword


def test_equip_armor_to_empty_slot(player_entity, leather_armor):
    """Equipping armor to empty slot succeeds."""
    equipment = player_entity.get_component(EquipmentComponent)
    previous = equipment.equip(leather_armor)
    assert previous is None


def test_equip_armor_updates_slot(player_entity, leather_armor):
    """Equipping armor updates the armor slot."""
    equipment = player_entity.get_component(EquipmentComponent)
    equipment.equip(leather_armor)
    assert equipment.get_equipped(EquipmentSlot.ARMOR) == leather_armor


def test_equip_multiple_items_different_slots(player_entity, iron_sword, leather_armor):
    """Equipping items in different slots both succeed."""
    equipment = player_entity.get_component(EquipmentComponent)
    equipment.equip(iron_sword)
    equipment.equip(leather_armor)
    assert len(equipment.get_all_equipped()) == 2


def test_equip_returns_previous_item(player_entity):
    """Equipping new weapon returns previously equipped weapon."""
    equipment = player_entity.get_component(EquipmentComponent)

    # Create two swords
    sword1 = ComponentEntity(Position(0, 0), "/", "Sword 1", False)
    sword1.add_component(EquipmentStats(EquipmentSlot.WEAPON, power_bonus=2))

    sword2 = ComponentEntity(Position(0, 0), "/", "Sword 2", False)
    sword2.add_component(EquipmentStats(EquipmentSlot.WEAPON, power_bonus=3))

    equipment.equip(sword1)
    previous = equipment.equip(sword2)
    assert previous == sword1


def test_equip_replaces_previous_item(player_entity):
    """Equipping new weapon replaces previous weapon in slot."""
    equipment = player_entity.get_component(EquipmentComponent)

    sword1 = ComponentEntity(Position(0, 0), "/", "Sword 1", False)
    sword1.add_component(EquipmentStats(EquipmentSlot.WEAPON, power_bonus=2))

    sword2 = ComponentEntity(Position(0, 0), "/", "Sword 2", False)
    sword2.add_component(EquipmentStats(EquipmentSlot.WEAPON, power_bonus=3))

    equipment.equip(sword1)
    equipment.equip(sword2)
    assert equipment.get_equipped(EquipmentSlot.WEAPON) == sword2


def test_unequip_removes_item(player_entity, iron_sword):
    """Unequipping removes item from slot."""
    equipment = player_entity.get_component(EquipmentComponent)
    equipment.equip(iron_sword)
    equipment.unequip(EquipmentSlot.WEAPON)
    assert equipment.get_equipped(EquipmentSlot.WEAPON) is None


def test_unequip_returns_item(player_entity, iron_sword):
    """Unequipping returns the unequipped item."""
    equipment = player_entity.get_component(EquipmentComponent)
    equipment.equip(iron_sword)
    unequipped = equipment.unequip(EquipmentSlot.WEAPON)
    assert unequipped == iron_sword


def test_unequip_empty_slot_returns_none(player_entity):
    """Unequipping empty slot returns None."""
    equipment = player_entity.get_component(EquipmentComponent)
    unequipped = equipment.unequip(EquipmentSlot.WEAPON)
    assert unequipped is None


def test_is_slot_empty_on_empty_slot(player_entity):
    """is_slot_empty returns True for empty slot."""
    equipment = player_entity.get_component(EquipmentComponent)
    assert equipment.is_slot_empty(EquipmentSlot.WEAPON) is True


def test_is_slot_empty_on_filled_slot(player_entity, iron_sword):
    """is_slot_empty returns False for filled slot."""
    equipment = player_entity.get_component(EquipmentComponent)
    equipment.equip(iron_sword)
    assert equipment.is_slot_empty(EquipmentSlot.WEAPON) is False


def test_get_equipped_empty_slot(player_entity):
    """get_equipped returns None for empty slot."""
    equipment = player_entity.get_component(EquipmentComponent)
    assert equipment.get_equipped(EquipmentSlot.WEAPON) is None


def test_get_all_equipped_empty():
    """get_all_equipped returns empty dict when nothing equipped."""
    equipment = EquipmentComponent()
    assert equipment.get_all_equipped() == {}


def test_get_all_equipped_with_items(player_entity, iron_sword, leather_armor):
    """get_all_equipped returns all equipped items."""
    equipment = player_entity.get_component(EquipmentComponent)
    equipment.equip(iron_sword)
    equipment.equip(leather_armor)
    all_equipped = equipment.get_all_equipped()
    assert EquipmentSlot.WEAPON in all_equipped
    assert EquipmentSlot.ARMOR in all_equipped


def test_total_power_bonus_no_equipment():
    """Total power bonus is 0 with no equipment."""
    equipment = EquipmentComponent()
    assert equipment.get_total_power_bonus() == 0


def test_total_power_bonus_one_item(player_entity, iron_sword):
    """Total power bonus equals weapon power bonus."""
    equipment = player_entity.get_component(EquipmentComponent)
    equipment.equip(iron_sword)
    # Iron sword has +3 power
    assert equipment.get_total_power_bonus() == 3


def test_total_defense_bonus_no_equipment():
    """Total defense bonus is 0 with no equipment."""
    equipment = EquipmentComponent()
    assert equipment.get_total_defense_bonus() == 0


def test_total_defense_bonus_one_item(player_entity, leather_armor):
    """Total defense bonus equals armor defense bonus."""
    equipment = player_entity.get_component(EquipmentComponent)
    equipment.equip(leather_armor)
    # Leather armor has +2 defense
    assert equipment.get_total_defense_bonus() == 2


def test_total_defense_bonus_multiple_items(player_entity, leather_armor, steel_helmet):
    """Total defense bonus sums multiple items."""
    equipment = player_entity.get_component(EquipmentComponent)
    equipment.equip(leather_armor)  # +2 defense
    equipment.equip(steel_helmet)  # +1 defense
    assert equipment.get_total_defense_bonus() == 3


def test_total_max_hp_bonus_no_equipment():
    """Total max HP bonus is 0 with no equipment."""
    equipment = EquipmentComponent()
    assert equipment.get_total_max_hp_bonus() == 0


def test_total_max_hp_bonus_with_helmet(player_entity, steel_helmet):
    """Total max HP bonus equals helmet HP bonus."""
    equipment = player_entity.get_component(EquipmentComponent)
    equipment.equip(steel_helmet)
    # Steel helmet has +5 max HP
    assert equipment.get_total_max_hp_bonus() == 5


def test_equip_item_without_equipment_stats_raises_error(player_entity):
    """Equipping item without EquipmentStats raises ValueError."""
    equipment = player_entity.get_component(EquipmentComponent)
    invalid_item = ComponentEntity(Position(0, 0), "X", "Invalid", False)

    with pytest.raises(ValueError, match="has no EquipmentStats component"):
        equipment.equip(invalid_item)


def test_equipment_stats_component_has_slot():
    """EquipmentStats component stores slot."""
    stats = EquipmentStats(EquipmentSlot.WEAPON, power_bonus=5)
    assert stats.slot == EquipmentSlot.WEAPON


def test_equipment_stats_component_has_power_bonus():
    """EquipmentStats component stores power bonus."""
    stats = EquipmentStats(EquipmentSlot.WEAPON, power_bonus=5)
    assert stats.power_bonus == 5


def test_equipment_stats_component_has_defense_bonus():
    """EquipmentStats component stores defense bonus."""
    stats = EquipmentStats(EquipmentSlot.ARMOR, defense_bonus=3)
    assert stats.defense_bonus == 3


def test_equipment_stats_component_has_max_hp_bonus():
    """EquipmentStats component stores max HP bonus."""
    stats = EquipmentStats(EquipmentSlot.HELMET, max_hp_bonus=10)
    assert stats.max_hp_bonus == 10


def test_equipment_stats_defaults_to_zero():
    """EquipmentStats defaults bonuses to 0."""
    stats = EquipmentStats(EquipmentSlot.WEAPON)
    assert stats.power_bonus == 0
    assert stats.defense_bonus == 0
    assert stats.max_hp_bonus == 0
