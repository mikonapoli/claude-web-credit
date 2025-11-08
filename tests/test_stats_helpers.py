"""Tests for stats helper functions."""

from roguelike.components.entity import ComponentEntity
from roguelike.components.equipment import EquipmentComponent, EquipmentStats, EquipmentSlot
from roguelike.components.helpers import get_equipment_bonuses
from roguelike.utils.position import Position


def test_get_equipment_bonuses_no_equipment():
    """Entity without EquipmentComponent returns zero bonuses."""
    entity = ComponentEntity(Position(0, 0), "@", "Test")
    power_bonus, defense_bonus, hp_bonus = get_equipment_bonuses(entity)

    assert power_bonus == 0
    assert defense_bonus == 0
    assert hp_bonus == 0


def test_get_equipment_bonuses_with_multiple_items():
    """Entity with multiple equipped items returns sum of bonuses."""
    entity = ComponentEntity(Position(0, 0), "@", "Test")
    entity.add_component(EquipmentComponent())

    # Equip weapon with power bonus
    weapon = ComponentEntity(Position(0, 0), "/", "Sword")
    weapon.add_component(EquipmentStats(EquipmentSlot.WEAPON, power_bonus=5))
    entity.get_component(EquipmentComponent).equip(weapon)

    # Equip armor with defense and hp bonuses
    armor = ComponentEntity(Position(0, 0), "[", "Armor")
    armor.add_component(EquipmentStats(EquipmentSlot.ARMOR, defense_bonus=3, max_hp_bonus=10))
    entity.get_component(EquipmentComponent).equip(armor)

    power_bonus, defense_bonus, hp_bonus = get_equipment_bonuses(entity)

    assert power_bonus == 5
    assert defense_bonus == 3
    assert hp_bonus == 10
