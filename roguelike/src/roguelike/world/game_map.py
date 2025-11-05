"""Game map implementation."""

import numpy as np
from numpy.typing import NDArray

from roguelike.utils.position import Position
from roguelike.world.tile import TileType, Tiles


class GameMap:
    """Represents the game world grid."""

    def __init__(self, width: int, height: int):
        """Initialize a map filled with walls.

        Args:
            width: Map width in tiles
            height: Map height in tiles
        """
        self.width = width
        self.height = height
        # Use numpy structured array for efficient tile storage
        self.tiles: NDArray = np.full((height, width), Tiles.WALL, dtype=object)

    def in_bounds(self, position: Position) -> bool:
        """Check if a position is within map bounds.

        Args:
            position: Position to check

        Returns:
            True if position is within bounds
        """
        return 0 <= position.x < self.width and 0 <= position.y < self.height

    def get_tile(self, position: Position) -> TileType:
        """Get tile at a position.

        Args:
            position: Position to query

        Returns:
            TileType at that position

        Raises:
            IndexError: If position is out of bounds
        """
        if not self.in_bounds(position):
            raise IndexError(f"Position {position} is out of bounds")
        return self.tiles[position.y, position.x]

    def set_tile(self, position: Position, tile_type: TileType) -> None:
        """Set tile at a position.

        Args:
            position: Position to set
            tile_type: Type of tile to place

        Raises:
            IndexError: If position is out of bounds
        """
        if not self.in_bounds(position):
            raise IndexError(f"Position {position} is out of bounds")
        self.tiles[position.y, position.x] = tile_type

    def is_walkable(self, position: Position) -> bool:
        """Check if a position is walkable.

        Args:
            position: Position to check

        Returns:
            True if position is walkable and in bounds
        """
        if not self.in_bounds(position):
            return False
        return self.get_tile(position).walkable

    def is_transparent(self, position: Position) -> bool:
        """Check if a position is transparent (doesn't block sight).

        Args:
            position: Position to check

        Returns:
            True if position is transparent and in bounds
        """
        if not self.in_bounds(position):
            return False
        return self.get_tile(position).transparent
