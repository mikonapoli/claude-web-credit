"""Mana component for magic-using entities."""

from roguelike.components.component import Component


class ManaComponent(Component):
    """Component for entity mana management."""

    def __init__(self, max_mp: int, mp_regen_rate: int = 1):
        """Initialize mana component.

        Args:
            max_mp: Maximum mana points
            mp_regen_rate: Mana regenerated per turn
        """
        super().__init__()
        self.max_mp = max_mp
        self._mp = max_mp
        self.mp_regen_rate = mp_regen_rate

    @property
    def mp(self) -> int:
        """Current mana points."""
        return self._mp

    @mp.setter
    def mp(self, value: int) -> None:
        """Set mana points, clamped between 0 and max_mp."""
        self._mp = max(0, min(value, self.max_mp))

    def has_mana(self, amount: int) -> bool:
        """Check if entity has enough mana.

        Args:
            amount: Mana amount to check

        Returns:
            True if entity has enough mana
        """
        return self._mp >= amount

    def consume_mana(self, amount: int) -> bool:
        """Consume mana if available.

        Args:
            amount: Mana to consume

        Returns:
            True if mana was consumed, False if insufficient
        """
        if not self.has_mana(amount):
            return False
        self._mp -= amount
        return True

    def restore_mana(self, amount: int) -> int:
        """Restore mana.

        Args:
            amount: Amount to restore

        Returns:
            Actual amount restored
        """
        old_mp = self._mp
        self.mp = self._mp + amount
        return self._mp - old_mp

    def regenerate(self) -> int:
        """Regenerate mana at the configured rate.

        Returns:
            Amount of mana regenerated
        """
        return self.restore_mana(self.mp_regen_rate)

    @property
    def mana_percentage(self) -> float:
        """Get mana as a percentage of max.

        Returns:
            Mana percentage (0.0 to 1.0)
        """
        if self.max_mp == 0:
            return 0.0
        return self._mp / self.max_mp
