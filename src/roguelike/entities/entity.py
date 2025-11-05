"""Base entity class for all game objects."""

from typing import Optional

from roguelike.utils.position import Position


class Entity:
    """Base class for all entities in the game world."""

    def __init__(
        self,
        position: Position,
        char: str,
        name: str,
        blocks_movement: bool = False,
    ):
        """Initialize an entity.

        Args:
            position: Current position in the game world
            char: ASCII character to display
            name: Entity name
            blocks_movement: Whether this entity blocks movement
        """
        self.position = position
        self.char = char
        self.name = name
        self.blocks_movement = blocks_movement

    def move(self, dx: int, dy: int) -> None:
        """Move entity by a relative offset.

        Args:
            dx: X offset
            dy: Y offset
        """
        self.position = Position(self.position.x + dx, self.position.y + dy)

    def move_to(self, position: Position) -> None:
        """Move entity to an absolute position.

        Args:
            position: New position
        """
        self.position = position

    def __repr__(self) -> str:
        """Return string representation."""
        return f"{self.__class__.__name__}(name={self.name!r}, pos={self.position})"
