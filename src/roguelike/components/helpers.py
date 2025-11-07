"""Helper functions for working with component-based entities."""

from typing import Optional

from roguelike.components.combat import CombatComponent
from roguelike.components.entity import ComponentEntity
from roguelike.components.health import HealthComponent
from roguelike.components.level import LevelComponent


def is_alive(entity: ComponentEntity) -> bool:
    """Check if an entity is alive.

    Args:
        entity: Entity to check

    Returns:
        True if entity has health and is alive, False otherwise
    """
    health = entity.get_component(HealthComponent)
    return health.is_alive if health else False


def get_hp(entity: ComponentEntity) -> Optional[int]:
    """Get current HP of an entity.

    Args:
        entity: Entity to check

    Returns:
        Current HP or None if entity has no health component
    """
    health = entity.get_component(HealthComponent)
    return health.hp if health else None


def get_max_hp(entity: ComponentEntity) -> Optional[int]:
    """Get max HP of an entity.

    Args:
        entity: Entity to check

    Returns:
        Max HP or None if entity has no health component
    """
    health = entity.get_component(HealthComponent)
    return health.max_hp if health else None


def get_power(entity: ComponentEntity) -> Optional[int]:
    """Get power stat of an entity.

    Args:
        entity: Entity to check

    Returns:
        Power or None if entity has no combat component
    """
    combat = entity.get_component(CombatComponent)
    return combat.power if combat else None


def get_defense(entity: ComponentEntity) -> Optional[int]:
    """Get defense stat of an entity.

    Args:
        entity: Entity to check

    Returns:
        Defense or None if entity has no combat component
    """
    combat = entity.get_component(CombatComponent)
    return combat.defense if combat else None


def get_level(entity: ComponentEntity) -> Optional[int]:
    """Get level of an entity.

    Args:
        entity: Entity to check

    Returns:
        Level or None if entity has no level component
    """
    level_comp = entity.get_component(LevelComponent)
    return level_comp.level if level_comp else None


def get_xp(entity: ComponentEntity) -> Optional[int]:
    """Get XP of an entity.

    Args:
        entity: Entity to check

    Returns:
        XP or None if entity has no level component
    """
    level_comp = entity.get_component(LevelComponent)
    return level_comp.xp if level_comp else None


def get_xp_value(entity: ComponentEntity) -> Optional[int]:
    """Get XP value of an entity (awarded when killed).

    Args:
        entity: Entity to check

    Returns:
        XP value or None if entity has no level component
    """
    level_comp = entity.get_component(LevelComponent)
    return level_comp.xp_value if level_comp else None


def is_player(entity) -> bool:
    """Check if an entity is the player.

    Args:
        entity: Entity to check (any type)

    Returns:
        True if entity is the player
    """
    # Check if it's a ComponentEntity and has player attributes
    if not isinstance(entity, ComponentEntity):
        return False
    return entity.name == "Player" and entity.char == "@"


def is_monster(entity) -> bool:
    """Check if an entity is a monster (has combat and health but not player).

    Args:
        entity: Entity to check (any type)

    Returns:
        True if entity is a monster
    """
    # Only ComponentEntity can be a monster
    if not isinstance(entity, ComponentEntity):
        return False

    return (
        entity.has_component(HealthComponent)
        and entity.has_component(CombatComponent)
        and not is_player(entity)
        and entity.blocks_movement
    )
