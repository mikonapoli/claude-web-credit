"""Position utilities for grid-based coordinates."""

from dataclasses import dataclass
from typing import Iterator


@dataclass(frozen=True)
class Position:
    """Immutable 2D grid position."""

    x: int
    y: int

    def __add__(self, other: "Position") -> "Position":
        """Add two positions together."""
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Position") -> "Position":
        """Subtract one position from another."""
        return Position(self.x - other.x, self.y - other.y)

    def distance_to(self, other: "Position") -> float:
        """Calculate Euclidean distance to another position."""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def manhattan_distance_to(self, other: "Position") -> int:
        """Calculate Manhattan distance to another position."""
        return abs(self.x - other.x) + abs(self.y - other.y)

    def neighbors(self, include_diagonals: bool = True) -> Iterator["Position"]:
        """Yield all neighboring positions."""
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),  # Cardinal directions
        ]
        if include_diagonals:
            directions += [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # Diagonals

        for dx, dy in directions:
            yield Position(self.x + dx, self.y + dy)
