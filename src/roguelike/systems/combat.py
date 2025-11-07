"""Combat system for handling attacks and damage."""

from dataclasses import dataclass

from roguelike.components.combat import CombatComponent
from roguelike.components.entity import ComponentEntity
from roguelike.components.health import HealthComponent


@dataclass
class CombatResult:
    """Result of a combat action."""

    attacker_name: str
    defender_name: str
    damage: int
    defender_died: bool


def calculate_damage(attacker: ComponentEntity, defender: ComponentEntity) -> int:
    """Calculate damage dealt from attacker to defender.

    Args:
        attacker: Attacking entity
        defender: Defending entity

    Returns:
        Damage amount after defense reduction
    """
    attacker_combat = attacker.get_component(CombatComponent)
    defender_combat = defender.get_component(CombatComponent)

    if not attacker_combat or not defender_combat:
        return 0

    damage = attacker_combat.power - defender_combat.defense
    return max(0, damage)  # Minimum 0 damage


def attack(attacker: ComponentEntity, defender: ComponentEntity) -> CombatResult:
    """Perform an attack from one entity to another.

    Args:
        attacker: The attacking entity
        defender: The defending entity

    Returns:
        CombatResult with details of the attack
    """
    damage = calculate_damage(attacker, defender)

    defender_health = defender.get_component(HealthComponent)
    if defender_health:
        defender_health.take_damage(damage)

    return CombatResult(
        attacker_name=attacker.name,
        defender_name=defender.name,
        damage=damage,
        defender_died=not defender_health.is_alive if defender_health else False,
    )
