"""Tests for Room class."""

from roguelike.utils.position import Position
from roguelike.world.room import Room


def test_room_creation():
    """Room can be created with dimensions."""
    room = Room(x=5, y=10, width=8, height=6)
    assert room.x == 5


def test_room_dimensions():
    """Room stores dimensions correctly."""
    room = Room(x=5, y=10, width=8, height=6)
    assert room.width == 8 and room.height == 6


def test_room_x2_coordinate():
    """Room calculates right edge correctly."""
    room = Room(x=5, y=10, width=8, height=6)
    assert room.x2 == 13


def test_room_y2_coordinate():
    """Room calculates bottom edge correctly."""
    room = Room(x=5, y=10, width=8, height=6)
    assert room.y2 == 16


def test_room_center():
    """Room calculates center position correctly."""
    room = Room(x=0, y=0, width=10, height=10)
    assert room.center == Position(5, 5)


def test_room_inner_tiles_count():
    """Room inner tiles excludes outer boundary."""
    room = Room(x=0, y=0, width=5, height=5)
    inner = list(room.inner_tiles())
    assert len(inner) == 16  # 4x4 inner area (width-1 x height-1)


def test_room_intersects_overlapping():
    """Overlapping rooms are detected."""
    room1 = Room(x=5, y=5, width=10, height=10)
    room2 = Room(x=10, y=10, width=10, height=10)
    assert room1.intersects(room2)


def test_room_intersects_separate():
    """Separate rooms do not intersect."""
    room1 = Room(x=0, y=0, width=5, height=5)
    room2 = Room(x=10, y=10, width=5, height=5)
    assert not room1.intersects(room2)


def test_room_intersects_touching():
    """Rooms that touch at edges intersect."""
    room1 = Room(x=0, y=0, width=5, height=5)
    room2 = Room(x=5, y=0, width=5, height=5)
    assert room1.intersects(room2)
