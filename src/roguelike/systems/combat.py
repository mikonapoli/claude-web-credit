"""Combat system for handling attacks and damage."""

from dataclasses import dataclass
from typing import Optional

from roguelike.entities.actor import Actor


@dataclass
class CombatResult:
    """Result of a combat action."""

    attacker_name: str
    defender_name: str
    damage: int
    defender_died: bool


def calculate_damage(
    attacker: Actor,
    defender: Actor,
    attacker_power_bonus: int = 0,
    defender_defense_bonus: int = 0,
) -> int:
    """Calculate damage dealt from attacker to defender.

    Args:
        attacker: Attacking actor
        defender: Defending actor
        attacker_power_bonus: Bonus power from status effects
        defender_defense_bonus: Bonus defense from status effects

    Returns:
        Damage amount after defense reduction
    """
    effective_power = attacker.power + attacker_power_bonus
    effective_defense = defender.defense + defender_defense_bonus
    damage = effective_power - effective_defense
    return max(0, damage)  # Minimum 0 damage


def attack(
    attacker: Actor,
    defender: Actor,
    attacker_power_bonus: int = 0,
    defender_defense_bonus: int = 0,
) -> CombatResult:
    """Perform an attack from one actor to another.

    Args:
        attacker: The attacking actor
        defender: The defending actor
        attacker_power_bonus: Bonus power from status effects
        defender_defense_bonus: Bonus defense from status effects

    Returns:
        CombatResult with details of the attack
    """
    damage = calculate_damage(
        attacker, defender, attacker_power_bonus, defender_defense_bonus
    )
    defender.take_damage(damage)

    return CombatResult(
        attacker_name=attacker.name,
        defender_name=defender.name,
        damage=damage,
        defender_died=not defender.is_alive,
    )
