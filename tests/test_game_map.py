"""Tests for GameMap."""

import pytest

from roguelike.utils.position import Position
from roguelike.world.game_map import GameMap
from roguelike.world.tile import Tiles


def test_map_creation():
    """Map is created with correct dimensions."""
    game_map = GameMap(80, 50)
    assert game_map.width == 80


def test_map_height():
    """Map stores height correctly."""
    game_map = GameMap(80, 50)
    assert game_map.height == 50


def test_map_initialized_with_walls():
    """New map is filled with wall tiles."""
    game_map = GameMap(10, 10)
    tile = game_map.get_tile(Position(5, 5))
    assert tile == Tiles.WALL


def test_in_bounds_valid_position():
    """Position within bounds returns True."""
    game_map = GameMap(10, 10)
    assert game_map.in_bounds(Position(5, 5))


def test_in_bounds_negative_x():
    """Negative x position is out of bounds."""
    game_map = GameMap(10, 10)
    assert not game_map.in_bounds(Position(-1, 5))


def test_in_bounds_exceeds_width():
    """Position exceeding width is out of bounds."""
    game_map = GameMap(10, 10)
    assert not game_map.in_bounds(Position(10, 5))


def test_in_bounds_exceeds_height():
    """Position exceeding height is out of bounds."""
    game_map = GameMap(10, 10)
    assert not game_map.in_bounds(Position(5, 10))


def test_set_and_get_tile():
    """Tile can be set and retrieved."""
    game_map = GameMap(10, 10)
    pos = Position(5, 5)
    game_map.set_tile(pos, Tiles.FLOOR)
    assert game_map.get_tile(pos) == Tiles.FLOOR


def test_get_tile_out_of_bounds():
    """Getting tile out of bounds raises IndexError."""
    game_map = GameMap(10, 10)
    with pytest.raises(IndexError):
        game_map.get_tile(Position(20, 20))


def test_set_tile_out_of_bounds():
    """Setting tile out of bounds raises IndexError."""
    game_map = GameMap(10, 10)
    with pytest.raises(IndexError):
        game_map.set_tile(Position(20, 20), Tiles.FLOOR)


def test_is_walkable_floor():
    """Floor tile is walkable."""
    game_map = GameMap(10, 10)
    pos = Position(5, 5)
    game_map.set_tile(pos, Tiles.FLOOR)
    assert game_map.is_walkable(pos)


def test_is_walkable_wall():
    """Wall tile is not walkable."""
    game_map = GameMap(10, 10)
    pos = Position(5, 5)
    assert not game_map.is_walkable(pos)


def test_is_walkable_out_of_bounds():
    """Out of bounds position is not walkable."""
    game_map = GameMap(10, 10)
    assert not game_map.is_walkable(Position(20, 20))


def test_is_transparent_floor():
    """Floor tile is transparent."""
    game_map = GameMap(10, 10)
    pos = Position(5, 5)
    game_map.set_tile(pos, Tiles.FLOOR)
    assert game_map.is_transparent(pos)


def test_is_transparent_wall():
    """Wall tile is not transparent."""
    game_map = GameMap(10, 10)
    pos = Position(5, 5)
    assert not game_map.is_transparent(pos)
