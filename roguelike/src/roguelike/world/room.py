"""Rectangular room for dungeon generation."""

from dataclasses import dataclass
from typing import Iterator

from roguelike.utils.position import Position


@dataclass
class Room:
    """A rectangular room in the dungeon."""

    x: int  # Top-left corner x
    y: int  # Top-left corner y
    width: int
    height: int

    @property
    def x2(self) -> int:
        """Right edge x coordinate."""
        return self.x + self.width

    @property
    def y2(self) -> int:
        """Bottom edge y coordinate."""
        return self.y + self.height

    @property
    def center(self) -> Position:
        """Center position of the room."""
        return Position(
            x=(self.x + self.x2) // 2,
            y=(self.y + self.y2) // 2
        )

    def inner_tiles(self) -> Iterator[Position]:
        """Yield all inner (non-wall) tile positions."""
        for y in range(self.y + 1, self.y2):
            for x in range(self.x + 1, self.x2):
                yield Position(x, y)

    def intersects(self, other: "Room") -> bool:
        """Check if this room intersects with another.

        Args:
            other: Another room

        Returns:
            True if rooms overlap
        """
        return (
            self.x <= other.x2
            and self.x2 >= other.x
            and self.y <= other.y2
            and self.y2 >= other.y
        )
