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

    Accounts for status effect bonuses:
    - Gigantism: +3 power (attacker)
    - Rubber Chicken: +1 power (attacker)
    - Shrinking: +2 defense (defender)

    Args:
        attacker: Attacking actor
        defender: Defending actor

    Returns:
        Damage amount after defense reduction
    """
    # Calculate effective power with status effect bonuses
    attacker_power = attacker.power
    if hasattr(attacker, "_status_effects"):
        effects = attacker._status_effects
        if effects.has_effect("gigantism"):
            attacker_power += effects.get_effect("gigantism").power
        if effects.has_effect("rubber_chicken"):
            attacker_power += effects.get_effect("rubber_chicken").power

    # Calculate effective defense with status effect bonuses
    defender_defense = defender.defense
    if hasattr(defender, "_status_effects"):
        effects = defender._status_effects
        if effects.has_effect("shrinking"):
            defender_defense += effects.get_effect("shrinking").power

    damage = attacker_power - defender_defense
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
