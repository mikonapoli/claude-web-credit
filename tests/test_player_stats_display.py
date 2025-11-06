"""Tests for enhanced player stats display integration."""

import pytest

from roguelike.components.equipment import EquipmentSlot, EquipmentStats
from roguelike.components.entity import ComponentEntity
from roguelike.components.status_effects import StatusEffect
from roguelike.entities.player import Player
from roguelike.systems.combat import get_effective_power, get_effective_defense
from roguelike.utils.position import Position


def test_player_has_equipment_component():
    """Player entity has equipment component."""
    player = Player(Position(0, 0))
    assert hasattr(player, "equipment")
    assert player.equipment is not None


def test_player_has_mana_component():
    """Player entity has mana component."""
    player = Player(Position(0, 0))
    assert hasattr(player, "mana")
    assert player.mana is not None
    assert player.mana.max_mp == 20
    assert player.mana.mp == 20


def test_player_has_status_effects_component():
    """Player entity has status effects component."""
    player = Player(Position(0, 0))
    assert hasattr(player, "status_effects")
    assert player.status_effects is not None


def test_player_effective_power_without_equipment():
    """Player effective power equals base power without equipment."""
    player = Player(Position(0, 0))
    assert player.effective_power == player.power
    assert player.effective_power == 5  # Base power from Player init


def test_player_effective_defense_without_equipment():
    """Player effective defense equals base defense without equipment."""
    player = Player(Position(0, 0))
    assert player.effective_defense == player.defense
    assert player.effective_defense == 2  # Base defense from Player init


def test_player_effective_max_hp_without_equipment():
    """Player effective max HP equals base max HP without equipment."""
    player = Player(Position(0, 0))
    assert player.effective_max_hp == player.max_hp
    assert player.effective_max_hp == 30  # Base max HP from Player init


def test_player_effective_power_with_equipment():
    """Player effective power includes equipment bonuses."""
    player = Player(Position(0, 0))

    # Create a weapon with power bonus
    weapon = ComponentEntity(Position(0, 0), "sword", "/")
    weapon_stats = EquipmentStats(
        slot=EquipmentSlot.WEAPON,
        power_bonus=5
    )
    weapon.add_component(weapon_stats)

    # Equip the weapon
    player.equipment.equip(weapon)

    # Check effective power
    assert player.effective_power == 10  # 5 base + 5 from weapon


def test_player_effective_defense_with_equipment():
    """Player effective defense includes equipment bonuses."""
    player = Player(Position(0, 0))

    # Create armor with defense bonus
    armor = ComponentEntity(Position(0, 0), "armor", "[")
    armor_stats = EquipmentStats(
        slot=EquipmentSlot.ARMOR,
        defense_bonus=4
    )
    armor.add_component(armor_stats)

    # Equip the armor
    player.equipment.equip(armor)

    # Check effective defense
    assert player.effective_defense == 6  # 2 base + 4 from armor


def test_player_effective_max_hp_with_equipment():
    """Player effective max HP includes equipment bonuses."""
    player = Player(Position(0, 0))

    # Create armor with max HP bonus
    armor = ComponentEntity(Position(0, 0), "plate", "[")
    armor_stats = EquipmentStats(
        slot=EquipmentSlot.ARMOR,
        max_hp_bonus=10
    )
    armor.add_component(armor_stats)

    # Equip the armor
    player.equipment.equip(armor)

    # Check effective max HP
    assert player.effective_max_hp == 40  # 30 base + 10 from armor


def test_player_effective_stats_with_multiple_equipment():
    """Player effective stats include bonuses from multiple equipment."""
    player = Player(Position(0, 0))

    # Create and equip weapon
    weapon = ComponentEntity(Position(0, 0), "sword", "/")
    weapon.add_component(EquipmentStats(
        slot=EquipmentSlot.WEAPON,
        power_bonus=5
    ))
    player.equipment.equip(weapon)

    # Create and equip armor
    armor = ComponentEntity(Position(0, 0), "armor", "[")
    armor.add_component(EquipmentStats(
        slot=EquipmentSlot.ARMOR,
        defense_bonus=4,
        max_hp_bonus=10
    ))
    player.equipment.equip(armor)

    # Create and equip ring
    ring = ComponentEntity(Position(0, 0), "ring", "=")
    ring.add_component(EquipmentStats(
        slot=EquipmentSlot.RING,
        power_bonus=2,
        defense_bonus=1
    ))
    player.equipment.equip(ring)

    # Check all effective stats
    assert player.effective_power == 12  # 5 + 5 + 2
    assert player.effective_defense == 7  # 2 + 4 + 1
    assert player.effective_max_hp == 40  # 30 + 10


def test_combat_uses_effective_power():
    """Combat system uses player's effective power."""
    from roguelike.entities.actor import Actor

    player = Player(Position(0, 0))
    enemy = Actor(Position(1, 0), "o", "Orc", 10, 1, 3)

    # Initially player has base power of 5
    assert get_effective_power(player) == 5

    # Equip weapon with +5 power
    weapon = ComponentEntity(Position(0, 0), "sword", "/")
    weapon.add_component(EquipmentStats(
        slot=EquipmentSlot.WEAPON,
        power_bonus=5
    ))
    player.equipment.equip(weapon)

    # Now effective power should be 10
    assert get_effective_power(player) == 10


def test_combat_uses_effective_defense():
    """Combat system uses player's effective defense."""
    from roguelike.entities.actor import Actor

    player = Player(Position(0, 0))
    enemy = Actor(Position(1, 0), "o", "Orc", 10, 1, 3)

    # Initially player has base defense of 2
    assert get_effective_defense(player) == 2

    # Equip armor with +4 defense
    armor = ComponentEntity(Position(0, 0), "armor", "[")
    armor.add_component(EquipmentStats(
        slot=EquipmentSlot.ARMOR,
        defense_bonus=4
    ))
    player.equipment.equip(armor)

    # Now effective defense should be 6
    assert get_effective_defense(player) == 6


def test_combat_calculate_damage_with_equipment():
    """Combat damage calculation uses equipment bonuses."""
    from roguelike.entities.actor import Actor
    from roguelike.systems.combat import calculate_damage

    player = Player(Position(0, 0))
    enemy = Actor(Position(1, 0), "o", "Orc", 10, 2, 3)

    # Base damage: 5 power - 2 defense = 3
    base_damage = calculate_damage(player, enemy)
    assert base_damage == 3

    # Equip weapon with +5 power
    weapon = ComponentEntity(Position(0, 0), "sword", "/")
    weapon.add_component(EquipmentStats(
        slot=EquipmentSlot.WEAPON,
        power_bonus=5
    ))
    player.equipment.equip(weapon)

    # New damage: 10 power - 2 defense = 8
    new_damage = calculate_damage(player, enemy)
    assert new_damage == 8


def test_enemy_attack_uses_player_equipment_defense():
    """Enemy attacks are reduced by player's equipment defense."""
    from roguelike.entities.actor import Actor
    from roguelike.systems.combat import calculate_damage

    player = Player(Position(0, 0))
    enemy = Actor(Position(1, 0), "o", "Orc", 10, 2, 8)

    # Base damage enemy deals: 8 power - 2 defense = 6
    base_damage = calculate_damage(enemy, player)
    assert base_damage == 6

    # Equip armor with +4 defense
    armor = ComponentEntity(Position(0, 0), "armor", "[")
    armor.add_component(EquipmentStats(
        slot=EquipmentSlot.ARMOR,
        defense_bonus=4
    ))
    player.equipment.equip(armor)

    # New damage: 8 power - 6 defense = 2
    new_damage = calculate_damage(enemy, player)
    assert new_damage == 2


def test_player_mana_component_properties():
    """Player mana component has correct properties."""
    player = Player(Position(0, 0))

    assert player.mana.max_mp == 20
    assert player.mana.mp == 20
    assert player.mana.mp_regen_rate == 1
    assert player.mana.mana_percentage == 1.0


def test_player_can_consume_mana():
    """Player can consume mana for spells."""
    player = Player(Position(0, 0))

    # Consume some mana
    success = player.mana.consume_mana(5)
    assert success is True
    assert player.mana.mp == 15

    # Try to consume more than available
    success = player.mana.consume_mana(20)
    assert success is False
    assert player.mana.mp == 15  # Unchanged


def test_player_can_add_status_effects():
    """Player can have status effects applied."""
    player = Player(Position(0, 0))

    # Add poison effect
    player.status_effects.add_effect("poison", 5, power=2)
    assert player.status_effects.has_effect("poison")
    assert player.status_effects.get_effect_count() == 1

    # Add confusion effect
    player.status_effects.add_effect("confusion", 10)
    assert player.status_effects.has_effect("confusion")
    assert player.status_effects.get_effect_count() == 2


def test_player_status_effects_tick():
    """Player status effects duration decreases over time."""
    player = Player(Position(0, 0))

    # Add effect with 3 turn duration
    player.status_effects.add_effect("poison", 3, power=2)
    effect = player.status_effects.get_effect("poison")
    assert effect.duration == 3

    # Tick once
    expired = player.status_effects.tick_durations()
    assert len(expired) == 0
    effect = player.status_effects.get_effect("poison")
    assert effect.duration == 2

    # Tick twice more - effect should expire
    player.status_effects.tick_durations()
    expired = player.status_effects.tick_durations()
    assert "poison" in expired
    assert not player.status_effects.has_effect("poison")
