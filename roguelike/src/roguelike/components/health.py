"""Health component for entities."""

from roguelike.components.component import Component


class HealthComponent(Component):
    """Component for entity health management."""

    def __init__(self, max_hp: int):
        """Initialize health component.

        Args:
            max_hp: Maximum hit points
        """
        super().__init__()
        self.max_hp = max_hp
        self._hp = max_hp

    @property
    def hp(self) -> int:
        """Current hit points."""
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        """Set hit points, clamped between 0 and max_hp."""
        self._hp = max(0, min(value, self.max_hp))

    @property
    def is_alive(self) -> bool:
        """Check if entity is still alive."""
        return self._hp > 0

    def heal(self, amount: int) -> int:
        """Heal the entity.

        Args:
            amount: Amount to heal

        Returns:
            Actual amount healed
        """
        old_hp = self._hp
        self.hp = self._hp + amount
        return self._hp - old_hp

    def take_damage(self, amount: int) -> int:
        """Take damage.

        Args:
            amount: Damage amount

        Returns:
            Actual damage taken
        """
        old_hp = self._hp
        self.hp = self._hp - amount
        return old_hp - self._hp
