"""Status effects system for processing and managing status effects."""

from typing import Optional

from roguelike.components.entity import ComponentEntity
from roguelike.components.health import HealthComponent
from roguelike.components.status_effects import StatusEffectsComponent
from roguelike.engine.events import (
    EventBus,
    StatusEffectAppliedEvent,
    StatusEffectExpiredEvent,
    StatusEffectTickEvent,
)


class StatusEffectsSystem:
    """System for managing and processing status effects.

    Handles applying effects to entities, processing per-turn effects,
    and managing effect durations and expirations.
    """

    def __init__(self, event_bus: EventBus):
        """Initialize status effects system.

        Args:
            event_bus: Event bus for emitting status effect events
        """
        self.event_bus = event_bus

    def apply_effect(
        self,
        entity: ComponentEntity,
        effect_type: str,
        duration: int,
        power: int = 0,
        source: Optional[str] = None,
    ) -> bool:
        """Apply a status effect to an entity.

        Adds StatusEffectsComponent if needed.

        Args:
            entity: Entity to apply effect to
            effect_type: Type of effect (poison, confusion, invisibility, gigantism, shrinking, xp_bonus)
            duration: Number of turns the effect should last
            power: Effect strength (e.g., poison damage per turn, stat boost amount)
            source: Optional source of the effect

        Returns:
            True if effect was applied successfully
        """
        status_comp = entity.get_component(StatusEffectsComponent)
        if status_comp is None:
            status_comp = StatusEffectsComponent()
            entity.add_component(status_comp)

        # Check if this is a new effect (not a refresh)
        is_new = not status_comp.has_effect(effect_type)

        result = status_comp.add_effect(effect_type, duration, power, source)

        if result:
            # Apply immediate stat changes for stat-modifying effects (only on new application)
            if is_new:
                if effect_type == "gigantism":
                    entity.power += power
                elif effect_type == "shrinking":
                    entity.defense += power

            self.event_bus.emit(
                StatusEffectAppliedEvent(
                    entity_name=entity.name,
                    effect_type=effect_type,
                    duration=duration,
                    power=power,
                )
            )
        return result

    def process_effects(self, entity: ComponentEntity) -> bool:
        """Process all status effects on an entity for one turn.

        Applies per-turn effects (like poison damage), emits tick events,
        decrements durations, and removes expired effects.

        Args:
            entity: Entity whose effects to process

        Returns:
            True if the entity died from status effects
        """
        status_comp = entity.get_component(StatusEffectsComponent)
        if status_comp is None:
            return False

        entity_died = False

        # Process each active effect
        for effect in status_comp.get_all_effects():
            # Apply effect-specific behavior
            died = self._apply_effect_behavior(entity, effect.effect_type, effect.power)
            if died:
                entity_died = True
                # Don't process more effects if entity died
                break

            # Emit tick event
            self.event_bus.emit(
                StatusEffectTickEvent(
                    entity_name=entity.name,
                    effect_type=effect.effect_type,
                    power=effect.power,
                    remaining_duration=effect.duration - 1,
                )
            )

        # If entity died, clear all effects and don't tick durations
        if entity_died:
            status_comp.clear_all_effects()
            return True

        # Get effect data before ticking (for stat removal on expiration)
        effect_data = {
            effect.effect_type: effect.power
            for effect in status_comp.get_all_effects()
        }

        # Tick durations and get expired effects
        expired = status_comp.tick_durations()

        # Handle stat removal and emit expiration events
        for effect_type in expired:
            # Remove stat changes for stat-modifying effects
            power = effect_data.get(effect_type, 0)
            if effect_type == "gigantism":
                entity.power -= power
            elif effect_type == "shrinking":
                entity.defense -= power

            self.event_bus.emit(
                StatusEffectExpiredEvent(
                    entity_name=entity.name, effect_type=effect_type
                )
            )

        return False

    def _apply_effect_behavior(
        self, entity: ComponentEntity, effect_type: str, power: int
    ) -> bool:
        """Apply effect-specific behavior each turn.

        Args:
            entity: Entity affected
            effect_type: Type of effect to apply
            power: Effect strength

        Returns:
            True if the entity died from the effect
        """
        if effect_type == "poison":
            return self._apply_poison(entity, power)
        # Confusion and invisibility don't have per-turn damage
        # They are handled by checking has_effect in other systems
        return False

    def _apply_poison(self, entity: ComponentEntity, damage: int) -> bool:
        """Apply poison damage to an entity.

        Args:
            entity: Entity to damage
            damage: Amount of poison damage per turn

        Returns:
            True if the entity died from poison damage
        """
        if damage <= 0:
            return False

        health = entity.get_component(HealthComponent)
        if health:
            health.take_damage(damage)
            return not health.is_alive

        return False

    def has_effect(self, entity: ComponentEntity, effect_type: str) -> bool:
        """Check if entity has a specific status effect.

        Args:
            entity: Entity to check
            effect_type: Type of effect to check for

        Returns:
            True if entity has this effect active
        """
        status_comp = entity.get_component(StatusEffectsComponent)
        return status_comp is not None and status_comp.has_effect(effect_type)

    def remove_effect(self, entity: ComponentEntity, effect_type: str) -> bool:
        """Remove a status effect from an entity immediately.

        Args:
            entity: Entity to remove effect from
            effect_type: Type of effect to remove

        Returns:
            True if effect was removed
        """
        status_comp = entity.get_component(StatusEffectsComponent)
        if status_comp is None:
            return False

        # Get the effect power before removing (for stat removal)
        effect = status_comp.get_effect(effect_type)
        power = effect.power if effect else 0

        result = status_comp.remove_effect(effect_type)

        if result:
            # Remove stat changes for stat-modifying effects
            if effect_type == "gigantism":
                entity.power -= power
            elif effect_type == "shrinking":
                entity.defense -= power

            self.event_bus.emit(
                StatusEffectExpiredEvent(
                    entity_name=entity.name, effect_type=effect_type
                )
            )

        return result

    def get_effect_display(self, entity: ComponentEntity) -> list[str]:
        """Get display strings for all active effects.

        Args:
            entity: Entity to get effects for

        Returns:
            List of effect display strings (e.g., ["Poison (3)", "Confused (5)"])
        """
        status_comp = entity.get_component(StatusEffectsComponent)
        if status_comp is None:
            return []

        display = []
        for effect in status_comp.get_all_effects():
            effect_name = effect.effect_type.capitalize()
            display.append(f"{effect_name} ({effect.duration})")

        return display
