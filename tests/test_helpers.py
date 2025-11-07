"""Shared test helper functions for creating test entities."""

from roguelike.components.combat import CombatComponent
from roguelike.components.entity import ComponentEntity
from roguelike.components.health import HealthComponent
from roguelike.components.inventory import InventoryComponent
from roguelike.components.level import LevelComponent
from roguelike.utils.position import Position


def create_test_entity(
    pos: Position,
    char: str,
    name: str,
    max_hp: int = 10,
    defense: int = 0,
    power: int = 1,
    blocks_movement: bool = True,
    xp_value: int = 0,
    level: int = 1,
) -> ComponentEntity:
    """Helper to create a test entity with standard components.

    Args:
        pos: Position
        char: Display character
        name: Entity name
        max_hp: Maximum hit points
        defense: Defense value
        power: Attack power
        blocks_movement: Whether entity blocks movement
        xp_value: XP awarded when killed
        level: Entity level

    Returns:
        ComponentEntity with health, combat, and level components
    """
    entity = ComponentEntity(pos, char, name, blocks_movement=blocks_movement)
    entity.add_component(HealthComponent(max_hp=max_hp))
    entity.add_component(CombatComponent(power=power, defense=defense))
    entity.add_component(LevelComponent(level=level, xp=0, xp_value=xp_value))
    return entity


def create_test_player(pos: Position) -> ComponentEntity:
    """Create a test player entity.

    Args:
        pos: Starting position

    Returns:
        Player entity with standard components
    """
    player = create_test_entity(
        pos, "@", "Player",
        max_hp=30, defense=2, power=5,
        xp_value=0, level=1
    )
    player.add_component(InventoryComponent(capacity=26))
    return player


def create_test_monster(pos: Position, name: str = "Monster", max_hp: int = 10, power: int = 3, defense: int = 0, xp_value: int = 35) -> ComponentEntity:
    """Create a test monster entity.

    Args:
        pos: Starting position
        name: Monster name
        max_hp: Maximum hit points
        power: Attack power
        defense: Defense value
        xp_value: XP awarded when killed

    Returns:
        Monster entity with standard components
    """
    return create_test_entity(
        pos, "m", name,
        max_hp=max_hp, defense=defense, power=power,
        xp_value=xp_value, level=1
    )
