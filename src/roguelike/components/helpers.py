"""Helper functions for working with component-based entities.

This module provides high-level helper functions for common entity queries.
These functions abstract away component access patterns for specific use cases.

Note: For simple property access (hp, power, defense, etc.), use the
ComponentEntity properties directly (e.g., entity.hp, entity.power).
"""

from typing import Tuple

from roguelike.components.combat import CombatComponent
from roguelike.components.entity import ComponentEntity
from roguelike.components.equipment import EquipmentComponent
from roguelike.components.health import HealthComponent


def is_alive(entity: ComponentEntity) -> bool:
    """Check if an entity is alive.

    This is a convenience function that safely checks for health component
    existence before checking the is_alive status.

    Args:
        entity: Entity to check

    Returns:
        True if entity has health and is alive, False otherwise

    Note:
        For entities known to have HealthComponent, prefer using
        entity.is_alive property directly.
    """
    health = entity.get_component(HealthComponent)
    return health.is_alive if health else False


def is_player(entity) -> bool:
    """Check if an entity is the player.

    This function uses a heuristic based on entity name and character.
    It provides a centralized place to define what constitutes a player entity.

    Args:
        entity: Entity to check (any type)

    Returns:
        True if entity is the player

    Note:
        Currently identifies players by name="Player" and char="@".
        If player identification logic needs to change, update it here.
    """
    # Check if it's a ComponentEntity and has player attributes
    if not isinstance(entity, ComponentEntity):
        return False
    return entity.name == "Player" and entity.char == "@"


def is_monster(entity) -> bool:
    """Check if an entity is a monster.

    A monster is defined as a ComponentEntity that:
    - Has both HealthComponent and CombatComponent
    - Is not the player
    - Blocks movement

    This provides a centralized definition for monster identification
    used throughout systems (AI, rendering, combat).

    Args:
        entity: Entity to check (any type)

    Returns:
        True if entity is a monster

    Example:
        >>> for entity in entities:
        ...     if is_monster(entity) and is_alive(entity):
        ...         process_monster_ai(entity)
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


def get_effective_power(entity: ComponentEntity) -> int:
    """Calculate effective power (base power + equipment bonuses).

    Args:
        entity: Entity to calculate effective power for

    Returns:
        Total effective power including equipment bonuses

    Note:
        If entity has no CombatComponent, returns 0.
        If entity has no EquipmentComponent, returns base power.
    """
    combat = entity.get_component(CombatComponent)
    if not combat:
        return 0

    base_power = combat.power
    equipment = entity.get_component(EquipmentComponent)

    if equipment:
        return base_power + equipment.get_total_power_bonus()
    return base_power


def get_effective_defense(entity: ComponentEntity) -> int:
    """Calculate effective defense (base defense + equipment bonuses).

    Args:
        entity: Entity to calculate effective defense for

    Returns:
        Total effective defense including equipment bonuses

    Note:
        If entity has no CombatComponent, returns 0.
        If entity has no EquipmentComponent, returns base defense.
    """
    combat = entity.get_component(CombatComponent)
    if not combat:
        return 0

    base_defense = combat.defense
    equipment = entity.get_component(EquipmentComponent)

    if equipment:
        return base_defense + equipment.get_total_defense_bonus()
    return base_defense


def get_equipment_bonuses(entity: ComponentEntity) -> Tuple[int, int, int]:
    """Get all equipment bonuses for an entity.

    Args:
        entity: Entity to get equipment bonuses for

    Returns:
        Tuple of (power_bonus, defense_bonus, max_hp_bonus)

    Note:
        Returns (0, 0, 0) if entity has no EquipmentComponent.
    """
    equipment = entity.get_component(EquipmentComponent)
    if not equipment:
        return (0, 0, 0)

    return (
        equipment.get_total_power_bonus(),
        equipment.get_total_defense_bonus(),
        equipment.get_total_max_hp_bonus(),
    )
