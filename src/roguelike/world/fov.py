"""Field of view calculations."""

import numpy as np
import tcod.map
from numpy.typing import NDArray

from roguelike.utils.position import Position
from roguelike.world.game_map import GameMap


class FOVMap:
    """Manages field of view calculations."""

    def __init__(self, game_map: GameMap):
        """Initialize FOV map from game map.

        Args:
            game_map: The game map
        """
        self.width = game_map.width
        self.height = game_map.height

        # Create transparency map for FOV calculation
        self.transparency = np.zeros((game_map.height, game_map.width), dtype=bool)
        for y in range(game_map.height):
            for x in range(game_map.width):
                pos = Position(x, y)
                self.transparency[y, x] = game_map.is_transparent(pos)

        # Visible tiles
        self.visible: NDArray = np.zeros((game_map.height, game_map.width), dtype=bool)

        # Explored tiles (player has seen at some point)
        self.explored: NDArray = np.zeros((game_map.height, game_map.width), dtype=bool)

    def compute_fov(self, position: Position, radius: int = 8) -> None:
        """Compute field of view from a position.

        Args:
            position: Center position for FOV
            radius: FOV radius
        """
        # Reset visible tiles
        self.visible[:] = False

        # Compute FOV using tcod (using default algorithm)
        # Note: pov expects (y, x) order to match numpy array indexing
        self.visible[:] = tcod.map.compute_fov(
            transparency=self.transparency,
            pov=(position.y, position.x),
            radius=radius,
        )

        # Mark visible tiles as explored
        self.explored |= self.visible

    def is_visible(self, position: Position) -> bool:
        """Check if a position is currently visible.

        Args:
            position: Position to check

        Returns:
            True if position is visible
        """
        if not (0 <= position.x < self.width and 0 <= position.y < self.height):
            return False
        return self.visible[position.y, position.x]

    def is_explored(self, position: Position) -> bool:
        """Check if a position has been explored.

        Args:
            position: Position to check

        Returns:
            True if position has been explored
        """
        if not (0 <= position.x < self.width and 0 <= position.y < self.height):
            return False
        return self.explored[position.y, position.x]
