"""Spell effect implementations."""

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from roguelike.utils.protocols import Combatant


@runtime_checkable
class SpellEffect(Protocol):
    """Protocol for spell effects."""

    def apply(self, caster: Combatant, target: Combatant, power: int) -> "EffectResult":
        """Apply the spell effect.

        Args:
            caster: Entity casting the spell
            target: Target of the effect
            power: Spell power value

        Returns:
            Result of applying the effect
        """
        ...


@dataclass
class EffectResult:
    """Result of applying a spell effect."""

    success: bool
    message: str
    damage_dealt: int = 0
    healing_done: int = 0
    target_died: bool = False


class DamageEffect:
    """Deals damage to the target."""

    def apply(self, caster: Combatant, target: Combatant, power: int) -> EffectResult:
        """Apply damage to target.

        Args:
            caster: Entity casting the spell
            target: Target of the effect
            power: Spell power (damage amount)

        Returns:
            Result of damage application
        """
        # Apply damage (ignoring defense for magic damage)
        actual_damage = target.take_damage(power)
        target_died = not target.is_alive

        caster_name = caster.name
        target_name = target.name

        if target_died:
            message = f"{caster_name}'s spell kills {target_name}!"
        else:
            message = f"{caster_name}'s spell hits {target_name} for {actual_damage} damage!"

        return EffectResult(
            success=True,
            message=message,
            damage_dealt=actual_damage,
            target_died=target_died,
        )


class HealEffect:
    """Heals the target."""

    def apply(self, caster: Combatant, target: Combatant, power: int) -> EffectResult:
        """Apply healing to target.

        Args:
            caster: Entity casting the spell
            target: Target of the effect
            power: Spell power (healing amount)

        Returns:
            Result of healing application
        """
        # Check if target has heal method (actors do, but protocol doesn't require it)
        if not hasattr(target, "heal"):
            return EffectResult(
                success=False,
                message=f"{target.name} cannot be healed!",
            )

        actual_healing = target.heal(power)  # type: ignore

        caster_name = caster.name
        target_name = target.name

        if actual_healing > 0:
            if caster == target:
                message = f"{caster_name} heals for {actual_healing} HP!"
            else:
                message = f"{caster_name} heals {target_name} for {actual_healing} HP!"
        else:
            message = f"{target_name} is already at full health!"

        return EffectResult(
            success=actual_healing > 0,
            message=message,
            healing_done=actual_healing,
        )


class BuffEffect:
    """Temporarily increases target's power."""

    def __init__(self, buff_amount: int = 2):
        """Initialize buff effect.

        Args:
            buff_amount: Amount to increase power by
        """
        self.buff_amount = buff_amount

    def apply(self, caster: Combatant, target: Combatant, power: int) -> EffectResult:
        """Apply power buff to target.

        Args:
            caster: Entity casting the spell
            target: Target of the effect
            power: Spell power (affects buff duration in real implementation)

        Returns:
            Result of buff application
        """
        # Note: This is a simplified version. A full implementation would
        # need a buff/debuff system with duration tracking.
        target.power += self.buff_amount

        caster_name = caster.name
        target_name = target.name

        if caster == target:
            message = f"{caster_name} feels empowered! (+{self.buff_amount} power)"
        else:
            message = f"{caster_name} empowers {target_name}! (+{self.buff_amount} power)"

        return EffectResult(
            success=True,
            message=message,
        )
