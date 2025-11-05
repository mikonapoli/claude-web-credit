"""Tile types for the game world."""

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class TileType:
    """Defines properties of a tile type."""

    walkable: bool
    transparent: bool  # Blocks line of sight?
    char: str  # ASCII character
    name: str


# Tile type definitions
class Tiles:
    """Collection of all tile types."""

    FLOOR: ClassVar[TileType] = TileType(
        walkable=True,
        transparent=True,
        char=".",
        name="floor"
    )

    WALL: ClassVar[TileType] = TileType(
        walkable=False,
        transparent=False,
        char="#",
        name="wall"
    )

    DOOR_CLOSED: ClassVar[TileType] = TileType(
        walkable=False,
        transparent=False,
        char="+",
        name="closed door"
    )

    DOOR_OPEN: ClassVar[TileType] = TileType(
        walkable=True,
        transparent=True,
        char="'",
        name="open door"
    )

    STAIRS_DOWN: ClassVar[TileType] = TileType(
        walkable=True,
        transparent=True,
        char=">",
        name="stairs down"
    )

    STAIRS_UP: ClassVar[TileType] = TileType(
        walkable=True,
        transparent=True,
        char="<",
        name="stairs up"
    )
