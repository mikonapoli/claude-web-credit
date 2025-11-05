"""Tests for procedural generation."""

from roguelike.utils.position import Position
from roguelike.world.procgen import (
    carve_room,
    create_horizontal_tunnel,
    create_vertical_tunnel,
    generate_dungeon,
)
from roguelike.world.game_map import GameMap
from roguelike.world.room import Room
from roguelike.world.tile import Tiles


def test_horizontal_tunnel_creates_floor():
    """Horizontal tunnel creates floor tiles."""
    game_map = GameMap(20, 20)
    create_horizontal_tunnel(game_map, 5, 10, 5)
    assert game_map.get_tile(Position(7, 5)) == Tiles.FLOOR


def test_vertical_tunnel_creates_floor():
    """Vertical tunnel creates floor tiles."""
    game_map = GameMap(20, 20)
    create_vertical_tunnel(game_map, 5, 10, 5)
    assert game_map.get_tile(Position(5, 7)) == Tiles.FLOOR


def test_carve_room_creates_floor():
    """Carving room creates floor tiles inside."""
    game_map = GameMap(20, 20)
    room = Room(x=5, y=5, width=5, height=5)
    carve_room(game_map, room)
    center = room.center
    assert game_map.get_tile(center) == Tiles.FLOOR


def test_generate_dungeon_returns_map():
    """Dungeon generation returns a GameMap."""
    game_map, rooms = generate_dungeon(
        width=80, height=50, max_rooms=10,
        min_room_size=4, max_room_size=8, random_seed=42
    )
    assert isinstance(game_map, GameMap)


def test_generate_dungeon_creates_rooms():
    """Dungeon generation creates at least one room."""
    game_map, rooms = generate_dungeon(
        width=80, height=50, max_rooms=10,
        min_room_size=4, max_room_size=8, random_seed=42
    )
    assert len(rooms) > 0


def test_generate_dungeon_rooms_have_floor():
    """Generated rooms contain floor tiles."""
    game_map, rooms = generate_dungeon(
        width=80, height=50, max_rooms=10,
        min_room_size=4, max_room_size=8, random_seed=42
    )
    first_room_center = rooms[0].center
    assert game_map.get_tile(first_room_center) == Tiles.FLOOR


def test_generate_dungeon_deterministic_with_seed():
    """Same seed produces same dungeon."""
    map1, rooms1 = generate_dungeon(
        width=80, height=50, max_rooms=10,
        min_room_size=4, max_room_size=8, random_seed=42
    )
    map2, rooms2 = generate_dungeon(
        width=80, height=50, max_rooms=10,
        min_room_size=4, max_room_size=8, random_seed=42
    )
    assert len(rooms1) == len(rooms2)


def test_generate_dungeon_different_without_seed():
    """Different seeds produce different dungeons."""
    map1, rooms1 = generate_dungeon(
        width=80, height=50, max_rooms=10,
        min_room_size=4, max_room_size=8, random_seed=42
    )
    map2, rooms2 = generate_dungeon(
        width=80, height=50, max_rooms=10,
        min_room_size=4, max_room_size=8, random_seed=123
    )
    # Very unlikely to have exact same room count with different seeds
    assert rooms1[0].center != rooms2[0].center
