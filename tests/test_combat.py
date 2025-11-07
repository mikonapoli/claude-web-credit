"""Tests for combat system."""

from roguelike.components.combat import CombatComponent
from roguelike.components.entity import ComponentEntity
from roguelike.components.health import HealthComponent
from roguelike.systems.combat import attack, calculate_damage
from roguelike.utils.position import Position


def create_test_entity(pos: Position, char: str, name: str, max_hp: int, defense: int, power: int) -> ComponentEntity:
    """Helper to create a test entity with combat components."""
    entity = ComponentEntity(pos, char, name, blocks_movement=True)
    entity.add_component(HealthComponent(max_hp=max_hp))
    entity.add_component(CombatComponent(power=power, defense=defense))
    return entity


def test_calculate_damage():
    """Damage is calculated as power minus defense."""
    attacker = create_test_entity(Position(0, 0), "@", "Attacker", max_hp=10, defense=0, power=5)
    defender = create_test_entity(Position(1, 1), "d", "Defender", max_hp=10, defense=2, power=1)
    damage = calculate_damage(attacker, defender)
    assert damage == 3  # 5 - 2


def test_calculate_damage_minimum_zero():
    """Damage cannot be negative."""
    attacker = create_test_entity(Position(0, 0), "@", "Weak", max_hp=10, defense=0, power=1)
    defender = create_test_entity(Position(1, 1), "d", "Armored", max_hp=10, defense=5, power=1)
    damage = calculate_damage(attacker, defender)
    assert damage == 0


def test_attack_deals_damage():
    """Attack reduces defender HP."""
    attacker = create_test_entity(Position(0, 0), "@", "Attacker", max_hp=10, defense=0, power=5)
    defender = create_test_entity(Position(1, 1), "d", "Defender", max_hp=10, defense=0, power=1)
    result = attack(attacker, defender)
    assert defender.hp == 5  # 10 - 5


def test_attack_result_contains_damage():
    """Attack result includes damage amount."""
    attacker = create_test_entity(Position(0, 0), "@", "Attacker", max_hp=10, defense=0, power=5)
    defender = create_test_entity(Position(1, 1), "d", "Defender", max_hp=10, defense=2, power=1)
    result = attack(attacker, defender)
    assert result.damage == 3


def test_attack_result_contains_names():
    """Attack result includes attacker and defender names."""
    attacker = create_test_entity(Position(0, 0), "@", "Hero", max_hp=10, defense=0, power=5)
    defender = create_test_entity(Position(1, 1), "d", "Monster", max_hp=10, defense=0, power=1)
    result = attack(attacker, defender)
    assert result.attacker_name == "Hero" and result.defender_name == "Monster"


def test_attack_detects_death():
    """Attack result indicates if defender died."""
    attacker = create_test_entity(Position(0, 0), "@", "Attacker", max_hp=10, defense=0, power=15)
    defender = create_test_entity(Position(1, 1), "d", "Defender", max_hp=10, defense=0, power=1)
    result = attack(attacker, defender)
    assert result.defender_died


def test_attack_no_death_when_survives():
    """Attack result shows defender alive if they survive."""
    attacker = create_test_entity(Position(0, 0), "@", "Attacker", max_hp=10, defense=0, power=3)
    defender = create_test_entity(Position(1, 1), "d", "Defender", max_hp=10, defense=0, power=1)
    result = attack(attacker, defender)
    assert not result.defender_died
