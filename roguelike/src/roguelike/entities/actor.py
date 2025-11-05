"""Actor entities (player and monsters)."""

from typing import Optional

from roguelike.entities.entity import Entity
from roguelike.utils.position import Position


class Actor(Entity):
    """An entity that can perform actions (player or monster)."""

    def __init__(
        self,
        position: Position,
        char: str,
        name: str,
        max_hp: int,
        defense: int,
        power: int,
    ):
        """Initialize an actor.

        Args:
            position: Starting position
            char: Display character
            name: Actor name
            max_hp: Maximum hit points
            defense: Defense value (damage reduction)
            power: Attack power
        """
        super().__init__(position=position, char=char, name=name, blocks_movement=True)
        self.max_hp = max_hp
        self._hp = max_hp
        self.defense = defense
        self.power = power

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
        """Check if actor is still alive."""
        return self._hp > 0

    def heal(self, amount: int) -> int:
        """Heal the actor.

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
