"""Protocol definitions for decoupling system dependencies."""

from typing import Protocol

from roguelike.utils.position import Position


class Combatant(Protocol):
    """Protocol for entities that can participate in combat."""

    name: str
    power: int
    defense: int

    @property
    def is_alive(self) -> bool:
        """Check if combatant is alive."""
        ...

    def take_damage(self, amount: int) -> int:
        """Take damage and return actual damage taken."""
        ...


class Positionable(Protocol):
    """Protocol for entities with a position."""

    position: Position
    blocks_movement: bool

    def move(self, dx: int, dy: int) -> None:
        """Move by relative offset."""
        ...

    def move_to(self, position: Position) -> None:
        """Move to absolute position."""
        ...


class AIControlled(Protocol):
    """Protocol for entities controlled by AI."""

    position: Position
    blocks_movement: bool

    @property
    def is_alive(self) -> bool:
        """Check if entity is alive."""
        ...


class Levelable(Protocol):
    """Protocol for entities that can level up."""

    max_hp: int
    hp: int
    power: int
    defense: int
    level: int


class XPSource(Protocol):
    """Protocol for entities that award XP when killed."""

    xp_value: int

    @property
    def is_alive(self) -> bool:
        """Check if entity is alive."""
        ...


class HealthBarRenderable(Protocol):
    """Protocol for entities that can have health bars rendered."""

    position: Position
    hp: int
    max_hp: int

    @property
    def is_alive(self) -> bool:
        """Check if entity is alive."""
        ...


class StatsDisplayable(Protocol):
    """Protocol for entities that can have comprehensive stats displayed."""

    name: str
    hp: int
    max_hp: int
    power: int
    defense: int
    level: int
    xp: int

    @property
    def is_alive(self) -> bool:
        """Check if entity is alive."""
        ...
