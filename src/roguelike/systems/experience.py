"""Experience and leveling system."""

from dataclasses import dataclass


@dataclass
class LevelUp:
    """Result of leveling up."""

    new_level: int
    hp_increase: int
    power_increase: int
    defense_increase: int


def calculate_xp_for_level(level: int) -> int:
    """Calculate total XP needed to reach a level.

    Uses formula: 100 * level^2

    Args:
        level: Target level

    Returns:
        Total XP needed for that level
    """
    return 100 * (level ** 2)


def get_xp_to_next_level(current_xp: int, current_level: int) -> int:
    """Calculate XP needed for next level.

    Args:
        current_xp: Current total XP
        current_level: Current level

    Returns:
        XP needed to reach next level
    """
    next_level_xp = calculate_xp_for_level(current_level + 1)
    return next_level_xp - current_xp


def check_level_up(current_xp: int, current_level: int) -> bool:
    """Check if entity should level up.

    Args:
        current_xp: Current total XP
        current_level: Current level

    Returns:
        True if entity has enough XP to level up
    """
    return current_xp >= calculate_xp_for_level(current_level + 1)


def apply_level_up(actor, level_increases: dict[str, int]) -> LevelUp:
    """Apply level up to an actor.

    Args:
        actor: Actor to level up
        level_increases: Dict of stat increases (hp, power, defense)

    Returns:
        LevelUp result
    """
    hp_increase = level_increases.get("hp", 0)
    power_increase = level_increases.get("power", 0)
    defense_increase = level_increases.get("defense", 0)

    actor.max_hp += hp_increase
    actor.hp = actor.max_hp  # Heal to full on level up
    actor.power += power_increase
    actor.defense += defense_increase
    actor.level += 1

    return LevelUp(
        new_level=actor.level,
        hp_increase=hp_increase,
        power_increase=power_increase,
        defense_increase=defense_increase,
    )
