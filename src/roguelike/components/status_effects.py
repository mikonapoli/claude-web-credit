"""Status effects component for entities."""

from dataclasses import dataclass, field
from typing import Dict, Optional, List

from roguelike.components.component import Component


@dataclass
class StatusEffect:
    """Represents a single status effect on an entity.

    Attributes:
        effect_type: Type of effect (e.g., "poison", "confusion", "invisibility")
        duration: Remaining turns for this effect
        power: Effect strength/magnitude (e.g., poison damage per turn)
        source: Optional name of what applied this effect
    """
    effect_type: str
    duration: int
    power: int = 0
    source: Optional[str] = None


class StatusEffectsComponent(Component):
    """Component for managing status effects on entities.

    Tracks active status effects, their durations, and provides
    methods to add, remove, and query effects.

    Component Communication:
    ------------------------
    This component uses the SHARED STATE pattern:
    - StatusEffectsSystem reads/writes to this component
    - StatusEffectsSystem may modify HealthComponent (e.g., poison damage)
    - Processing happens at a specific point in turn order

    Processing Order Dependencies:
    ------------------------------
    IMPORTANT: StatusEffectsSystem.process_effects() modifies HealthComponent.
    This happens AFTER player/enemy actions but BEFORE the next action.
    Commands handle their own turn cycle processing to maintain proper order.

    Example Effect Types:
    - "poison": Deals damage per turn (modifies HealthComponent)
    - "confusion": AI behavior modifier (checked by AI system)
    - "invisibility": Rendering/targeting modifier (checked by relevant systems)

    See docs/COMPONENT_COMMUNICATION.md for more details.
    """

    def __init__(self):
        """Initialize status effects component with empty effect list."""
        super().__init__()
        self._active_effects: Dict[str, StatusEffect] = {}

    def add_effect(self, effect_type: str, duration: int, power: int = 0,
                   source: Optional[str] = None) -> bool:
        """Add or refresh a status effect.

        If the effect already exists, updates to the longer duration.

        Args:
            effect_type: Type of effect to add
            duration: Number of turns the effect should last
            power: Effect strength (e.g., poison damage per turn)
            source: Optional source of the effect

        Returns:
            True if effect was added/refreshed, False if duration <= 0
        """
        if duration <= 0:
            return False

        # If effect exists, take the longer duration
        if effect_type in self._active_effects:
            existing = self._active_effects[effect_type]
            existing.duration = max(existing.duration, duration)
            existing.power = max(existing.power, power)
        else:
            self._active_effects[effect_type] = StatusEffect(
                effect_type=effect_type,
                duration=duration,
                power=power,
                source=source
            )

        return True

    def remove_effect(self, effect_type: str) -> bool:
        """Remove a status effect immediately.

        Args:
            effect_type: Type of effect to remove

        Returns:
            True if effect was removed, False if it didn't exist
        """
        if effect_type in self._active_effects:
            del self._active_effects[effect_type]
            return True
        return False

    def has_effect(self, effect_type: str) -> bool:
        """Check if entity has a specific effect.

        Args:
            effect_type: Type of effect to check for

        Returns:
            True if entity has this effect active
        """
        return effect_type in self._active_effects

    def get_effect(self, effect_type: str) -> Optional[StatusEffect]:
        """Get details of a specific effect.

        Args:
            effect_type: Type of effect to get

        Returns:
            StatusEffect if found, None otherwise
        """
        return self._active_effects.get(effect_type)

    def get_all_effects(self) -> List[StatusEffect]:
        """Get list of all active effects.

        Returns:
            List of all active StatusEffect objects
        """
        return list(self._active_effects.values())

    def tick_durations(self) -> List[str]:
        """Decrement all effect durations by 1 turn.

        Returns:
            List of effect types that expired this turn
        """
        expired = []

        for effect_type, effect in list(self._active_effects.items()):
            effect.duration -= 1
            if effect.duration <= 0:
                expired.append(effect_type)
                del self._active_effects[effect_type]

        return expired

    def clear_all_effects(self) -> None:
        """Remove all status effects immediately."""
        self._active_effects.clear()

    def get_effect_count(self) -> int:
        """Get number of active effects.

        Returns:
            Count of active status effects
        """
        return len(self._active_effects)
