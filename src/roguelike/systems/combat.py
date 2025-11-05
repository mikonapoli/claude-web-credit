"""Combat system for handling attacks and damage."""

from dataclasses import dataclass

from roguelike.entities.actor import Actor


@dataclass
class CombatResult:
    """Result of a combat action."""

    attacker_name: str
    defender_name: str
    damage: int
    defender_died: bool


def calculate_damage(attacker: Actor, defender: Actor) -> int:
    """Calculate damage dealt from attacker to defender.

    Args:
        attacker: Attacking actor
        defender: Defending actor

    Returns:
        Damage amount after defense reduction
    """
    damage = attacker.power - defender.defense
    return max(0, damage)  # Minimum 0 damage


def attack(attacker: Actor, defender: Actor) -> CombatResult:
    """Perform an attack from one actor to another.

    Args:
        attacker: The attacking actor
        defender: The defending actor

    Returns:
        CombatResult with details of the attack
    """
    damage = calculate_damage(attacker, defender)
    defender.take_damage(damage)

    return CombatResult(
        attacker_name=attacker.name,
        defender_name=defender.name,
        damage=damage,
        defender_died=not defender.is_alive,
    )
