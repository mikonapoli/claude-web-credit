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


def get_effective_power(actor: Actor) -> int:
    """Get effective power for an actor.

    For Player entities, includes equipment bonuses.
    For other actors, returns base power.

    Args:
        actor: The actor to get power for

    Returns:
        Effective power value
    """
    if hasattr(actor, "effective_power"):
        return actor.effective_power
    return actor.power


def get_effective_defense(actor: Actor) -> int:
    """Get effective defense for an actor.

    For Player entities, includes equipment bonuses.
    For other actors, returns base defense.

    Args:
        actor: The actor to get defense for

    Returns:
        Effective defense value
    """
    if hasattr(actor, "effective_defense"):
        return actor.effective_defense
    return actor.defense


def calculate_damage(attacker: Actor, defender: Actor) -> int:
    """Calculate damage dealt from attacker to defender.

    Args:
        attacker: Attacking actor
        defender: Defending actor

    Returns:
        Damage amount after defense reduction
    """
    power = get_effective_power(attacker)
    defense = get_effective_defense(defender)
    damage = power - defense
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
