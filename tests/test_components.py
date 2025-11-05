"""Tests for component system."""

from roguelike.components.combat import CombatComponent
from roguelike.components.entity import ComponentEntity
from roguelike.components.health import HealthComponent
from roguelike.components.level import LevelComponent
from roguelike.utils.position import Position


def test_component_entity_creation():
    """ComponentEntity can be created."""
    entity = ComponentEntity(Position(5, 5), "@", "Player")
    assert entity.position == Position(5, 5)
    assert entity.char == "@"
    assert entity.name == "Player"


def test_add_health_component():
    """Can add HealthComponent to entity."""
    entity = ComponentEntity(Position(5, 5), "@", "Player")
    health = HealthComponent(max_hp=30)
    entity.add_component(health)

    assert entity.has_component(HealthComponent)


def test_get_health_component():
    """Can retrieve HealthComponent from entity."""
    entity = ComponentEntity(Position(5, 5), "@", "Player")
    health = HealthComponent(max_hp=30)
    entity.add_component(health)

    retrieved = entity.get_component(HealthComponent)
    assert retrieved is health


def test_health_component_initial_values():
    """HealthComponent initializes with correct values."""
    health = HealthComponent(max_hp=30)
    assert health.max_hp == 30
    assert health.hp == 30
    assert health.is_alive


def test_health_component_take_damage():
    """HealthComponent can take damage."""
    health = HealthComponent(max_hp=30)
    damage_taken = health.take_damage(10)

    assert damage_taken == 10
    assert health.hp == 20


def test_health_component_death():
    """HealthComponent correctly reports death."""
    health = HealthComponent(max_hp=30)
    health.take_damage(30)

    assert health.hp == 0
    assert not health.is_alive


def test_health_component_heal():
    """HealthComponent can heal."""
    health = HealthComponent(max_hp=30)
    health.take_damage(10)
    healed = health.heal(5)

    assert healed == 5
    assert health.hp == 25


def test_health_component_heal_clamps_to_max():
    """Healing cannot exceed max_hp."""
    health = HealthComponent(max_hp=30)
    health.take_damage(5)
    healed = health.heal(20)

    assert healed == 5
    assert health.hp == 30


def test_health_component_damage_clamps_to_zero():
    """Damage cannot reduce HP below 0."""
    health = HealthComponent(max_hp=30)
    damage_taken = health.take_damage(50)

    assert damage_taken == 30
    assert health.hp == 0


def test_add_combat_component():
    """Can add CombatComponent to entity."""
    entity = ComponentEntity(Position(5, 5), "o", "Orc")
    combat = CombatComponent(power=5, defense=0)
    entity.add_component(combat)

    assert entity.has_component(CombatComponent)


def test_combat_component_values():
    """CombatComponent stores correct values."""
    combat = CombatComponent(power=5, defense=2)
    assert combat.power == 5
    assert combat.defense == 2


def test_add_level_component():
    """Can add LevelComponent to entity."""
    entity = ComponentEntity(Position(5, 5), "@", "Player")
    level = LevelComponent(level=1, xp=0, xp_value=0)
    entity.add_component(level)

    assert entity.has_component(LevelComponent)


def test_level_component_values():
    """LevelComponent stores correct values."""
    level = LevelComponent(level=2, xp=150, xp_value=50)
    assert level.level == 2
    assert level.xp == 150
    assert level.xp_value == 50


def test_entity_with_multiple_components():
    """Entity can have multiple components."""
    entity = ComponentEntity(Position(5, 5), "@", "Player")
    health = HealthComponent(max_hp=30)
    combat = CombatComponent(power=5, defense=2)
    level = LevelComponent(level=1, xp=0, xp_value=0)

    entity.add_component(health)
    entity.add_component(combat)
    entity.add_component(level)

    assert entity.has_component(HealthComponent)
    assert entity.has_component(CombatComponent)
    assert entity.has_component(LevelComponent)


def test_remove_component():
    """Can remove component from entity."""
    entity = ComponentEntity(Position(5, 5), "@", "Player")
    health = HealthComponent(max_hp=30)
    entity.add_component(health)

    entity.remove_component(HealthComponent)
    assert not entity.has_component(HealthComponent)


def test_get_nonexistent_component():
    """Getting nonexistent component returns None."""
    entity = ComponentEntity(Position(5, 5), "@", "Player")
    health = entity.get_component(HealthComponent)

    assert health is None


def test_component_attached_to_entity():
    """Component knows which entity it's attached to."""
    entity = ComponentEntity(Position(5, 5), "@", "Player")
    health = HealthComponent(max_hp=30)
    entity.add_component(health)

    assert health.entity is entity


def test_entity_move():
    """ComponentEntity can move."""
    entity = ComponentEntity(Position(5, 5), "@", "Player")
    entity.move(1, 2)

    assert entity.position == Position(6, 7)


def test_entity_move_to():
    """ComponentEntity can move to absolute position."""
    entity = ComponentEntity(Position(5, 5), "@", "Player")
    entity.move_to(Position(10, 15))

    assert entity.position == Position(10, 15)


def test_entity_blocks_movement():
    """ComponentEntity can block movement."""
    entity = ComponentEntity(Position(5, 5), "@", "Player", blocks_movement=True)
    assert entity.blocks_movement


def test_entity_repr():
    """ComponentEntity has useful string representation."""
    entity = ComponentEntity(Position(5, 5), "@", "Player")
    entity.add_component(HealthComponent(max_hp=30))
    entity.add_component(CombatComponent(power=5, defense=2))

    repr_str = repr(entity)
    assert "Player" in repr_str
    assert "Position(x=5, y=5)" in repr_str
    assert "HealthComponent" in repr_str
    assert "CombatComponent" in repr_str
